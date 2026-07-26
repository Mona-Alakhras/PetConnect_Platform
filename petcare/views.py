from functools import wraps
 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
 
from .forms import MAX_IMAGES_PER_PET, PetForm, validate_pet_images
from .models import AdoptionRequest, Pet, PetImage, User
 
PETS_PER_PAGE = 8
DASHBOARD_PETS_PER_PAGE = 6
 
 
def owner_required(view_func):
    """Allow only signed-in users whose role is 'Owner' (or staff).
 
    Hiding a link in the navbar is presentation, not authorisation — every
    owner-only view goes through this decorator.
    """
 
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != 'Owner' and not request.user.is_staff:
            messages.error(
                request,
                "That area is only available to pet owner accounts."
            )
            return redirect('index')
        return view_func(request, *args, **kwargs)
 
    return _wrapped
 
 
def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
 
 
# ==========================================================================
# Public pages
# ==========================================================================
 
def index(request):
    # All four category counts in a single aggregate query.
    counts = Pet.objects.filter(status='Available').aggregate(
        dogs=Count('id', filter=Q(species='Dog')),
        cats=Count('id', filter=Q(species='Cat')),
        birds=Count('id', filter=Q(species='Bird')),
        others=Count('id', filter=Q(species='Other')),
    )
 
    featured_pets = (
        Pet.objects
        .filter(status='Available')
        .prefetch_related('images')[:3]
    )
 
    context = {
        'dogs_count': counts['dogs'],
        'cats_count': counts['cats'],
        'birds_count': counts['birds'],
        'others_count': counts['others'],
        'featured_pets': featured_pets,
    }
    return render(request, 'index.html', context)
 
 
def about_view(request):
    return render(request, 'about.html')
 
 
def browse_pets_view(request):
    pets_list = (
        Pet.objects
        .filter(status='Available')
        .prefetch_related('images')
    )
 
    # Filtering happens on the server so it stays correct across pages.
    valid_species = {value for value, _ in Pet.SPECIES_CHOICES}
    species_query = request.GET.get('species') or ''
    if species_query and species_query.capitalize() in valid_species:
        species_query = species_query.capitalize()
        pets_list = pets_list.filter(species=species_query)
    else:
        species_query = ''
 
    paginator = Paginator(pets_list, PETS_PER_PAGE)
    pets = paginator.get_page(request.GET.get('page'))
 
    context = {
        'pets': pets,
        'total_count': paginator.count,
        'selected_species': species_query,
        'species_choices': Pet.SPECIES_CHOICES,
    }
    return render(request, 'browse_pets.html', context)
 
 
def pet_detail_view(request, pet_id):
    pet = get_object_or_404(
        Pet.objects.select_related('owner').prefetch_related('images'),
        id=pet_id,
    )
 
    already_requested = False
    if request.user.is_authenticated:
        already_requested = AdoptionRequest.objects.filter(
            pet=pet, adopter=request.user
        ).exists()
 
    context = {
        'pet': pet,
        'already_requested': already_requested,
        'is_own_pet': request.user.is_authenticated and pet.owner_id == request.user.id,
    }
    return render(request, 'pet_detail.html', context)
 
 
# ==========================================================================
# Authentication
# ==========================================================================
 
def register(request):
    if request.user.is_authenticated:
        return redirect('index')
 
    if request.method == 'POST':
        errors = User.objects.register_validator(request.POST)
 
        if errors:
            for value in errors.values():
                messages.error(request, value)
            # Re-render instead of redirecting so the user keeps what they typed.
            return render(request, 'register.html', {
                'errors': errors,
                'form_data': request.POST,
            })
 
        User.objects.register_user(request.POST)
        messages.success(
            request,
            "Your account has been created successfully! Please log in."
        )
        return redirect('login')
 
    return render(request, 'register.html')
 
 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
 
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
        )
 
        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', {
                'form_data': request.POST,
            })
 
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
 
        # Honour ?next= only when it points back into this site.
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
 
        return redirect('dashboard' if user.role == 'Owner' else 'index')
 
    return render(request, 'login.html')
 
 
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
 
 
@require_POST
def api_forgot_password(request):
    form = PasswordResetForm({"email": request.POST.get("email", "")})
 
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        )
        # Same response whether or not the address exists — no account enumeration.
        return JsonResponse({
            "success": True,
            "message": "If an account exists for that address, a reset link is on its way.",
        })
 
    return JsonResponse({
        "success": False,
        "message": "Please enter a valid email address.",
    })
 
 
# ==========================================================================
# Owner dashboard
# ==========================================================================
 
@owner_required
def dashboard_view(request):
    if request.method == "POST":
        return _create_pet(request)
 
    user_pets = (
        Pet.objects
        .filter(owner=request.user)
        .prefetch_related('images')
    )
 
    paginator = Paginator(user_pets, DASHBOARD_PETS_PER_PAGE)
    pets_page_obj = paginator.get_page(request.GET.get('page'))
 
    incoming_requests = (
        AdoptionRequest.objects
        .filter(pet__owner=request.user)
        .select_related('pet', 'adopter')
        .prefetch_related('pet__images')
    )
 
    request_counts = incoming_requests.aggregate(
        pending=Count('id', filter=Q(status='Pending')),
        approved=Count('id', filter=Q(status='Approved')),
    )
 
    context = {
        'total_pets': paginator.count,
        'active_requests_count': request_counts['pending'],
        'approved_requests_count': request_counts['approved'],
        'pets': pets_page_obj,
        'recent_pets': user_pets[:3],
        'incoming_requests': incoming_requests,
        'max_images': MAX_IMAGES_PER_PET,
    }
    return render(request, 'dashboard.html', context)
 
 
def _create_pet(request):
    """Handle the "Add Pet" submission from the dashboard."""
    form = PetForm(request.POST)
    uploads = request.FILES.getlist('images')
 
    if not form.is_valid():
        for field, errors in form.errors.items():
            label = field.replace('_', ' ').capitalize()
            for error in errors:
                messages.error(request, f"{label}: {error}")
        return redirect('dashboard')
 
    try:
        images = validate_pet_images(uploads)
    except ValidationError as exc:
        for message in exc.messages:
            messages.error(request, message)
        return redirect('dashboard')
 
    with transaction.atomic():
        pet = form.save(commit=False)
        pet.owner = request.user
        pet.save()
 
        for uploaded in images:
            PetImage.objects.create(pet=pet, image=uploaded)
 
    messages.success(request, f"{pet.name} has been listed successfully.")
    return redirect('dashboard')
 
 
@owner_required
@require_POST
def delete_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet_name = pet.name
    pet.delete()
    messages.success(request, f"{pet_name} has been removed from your listings.")
    return redirect('dashboard')
 
 
@owner_required
@require_POST
def update_request_status(request, request_id, action):
    if action not in ('Approved', 'Rejected'):
        return JsonResponse(
            {"success": False, "message": "Unknown action."}, status=400
        )
 
    # Scoping by pet__owner is what stops one owner from acting on another
    # owner's adoption requests.
    adoption_req = get_object_or_404(
        AdoptionRequest.objects.select_related('pet'),
        id=request_id,
        pet__owner=request.user,
    )
 
    if adoption_req.status != 'Pending':
        return JsonResponse({
            "success": False,
            "message": f"This request was already {adoption_req.status.lower()}.",
            "status": adoption_req.status,
        }, status=409)
 
    with transaction.atomic():
        adoption_req.status = action
        adoption_req.save(update_fields=['status', 'updated_at'])
 
        if action == 'Approved':
            pet = adoption_req.pet
            pet.status = 'Adopted'
            pet.save(update_fields=['status'])
 
            # Everyone else who asked for this pet is turned down automatically.
            AdoptionRequest.objects.filter(
                pet=pet, status='Pending'
            ).exclude(pk=adoption_req.pk).update(status='Rejected')
 
    if not _is_ajax(request):
        messages.success(request, f"Request {action.lower()} successfully.")
        return redirect('dashboard')
 
    return JsonResponse({
        "success": True,
        "status": adoption_req.status,
        "pet_status": adoption_req.pet.status,
    })
 
 
# ==========================================================================
# Adoption requests
# ==========================================================================
 
@login_required
@require_POST
def adopt_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
 
    if pet.owner_id == request.user.id:
        messages.warning(request, "You cannot request to adopt your own pet.")
        return redirect('pet_detail', pet_id=pet.id)
 
    if not pet.is_available:
        messages.warning(request, f"{pet.name} has already found a home.")
        return redirect('pet_detail', pet_id=pet.id)
 
    message_text = (request.POST.get('message') or '').strip()
    if len(message_text) < 20:
        messages.error(
            request,
            "Please tell the owner a little more about yourself (at least 20 characters)."
        )
        return redirect('pet_detail', pet_id=pet.id)
 
    try:
        # The insert needs its own atomic block: once a statement fails, the
        # surrounding transaction cannot run more queries until it is rolled back.
        with transaction.atomic():
            AdoptionRequest.objects.create(
                pet=pet,
                adopter=request.user,
                message=message_text,
            )
    except IntegrityError:
        # The unique constraint caught a duplicate submission.
        messages.warning(request, "You have already submitted a request for this pet.")
    else:
        messages.success(
            request,
            f"Your adoption request for {pet.name} has been sent successfully!"
        )
 
    return redirect('pet_detail', pet_id=pet.id)
 
 
@login_required
def my_requests_view(request):
    my_requests = (
        AdoptionRequest.objects
        .filter(adopter=request.user)
        .select_related('pet')
        .prefetch_related('pet__images')
    )
 
    counts = my_requests.aggregate(
        pending=Count('id', filter=Q(status='Pending')),
        approved=Count('id', filter=Q(status='Approved')),
        rejected=Count('id', filter=Q(status='Rejected')),
    )
 
    context = {
        'my_requests': my_requests,
        'pending_requests_count': counts['pending'],
        'approved_requests_count': counts['approved'],
        'rejected_requests_count': counts['rejected'],
    }
    return render(request, 'my_requests.html', context)