from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, Pet, PetImage, AdoptionRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator  # تأكدي من استيراد هذه المكتبة في أعلى الملف
from django.db.models import Count, Q
 
def index(request):
    # حساب أعداد جميع الفئات بـ استعلام واحد فقط (Database Aggregation)
    counts = Pet.objects.filter(status='Available').aggregate(
        dogs=Count('id', filter=Q(species='Dog')),
        cats=Count('id', filter=Q(species='Cat')),
        birds=Count('id', filter=Q(species='Bird')),
        others=Count('id', filter=Q(species='Other'))
    )

    featured_pets = Pet.objects.filter(status='Available').prefetch_related('images').order_by('-id')[:4]
    
    context = {
        'dogs_count': counts['dogs'],
        'cats_count': counts['cats'],
        'birds_count': counts['birds'],
        'others_count': counts['others'],
        'featured_pets': featured_pets,
    }
    return render(request, 'index.html', context)
 
 
def pet_list(request):
    pets = Pet.objects.filter(status='Available')
    context = {
        'pets': pets,
    }
    return render(request, 'pet_list.html', context)
 
 
def pet_list_by_species(request, species):
    pets = Pet.objects.filter(species=species, status='Available')
    context = {
        'pets': pets,
        'selected_species': species,
    }
    return render(request, 'pet_list.html', context)
 
 
def register(request):
    if request.method == 'POST':
        errors = User.objects.register_validator(request.POST)
 
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('register')
 
        User.objects.register_user(request.POST)
        messages.success(request, "Your account has been created successfully! Please log in.")
        return redirect('login')
 
    return render(request, 'register.html')
 
 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
 
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
 
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
 
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name}!")
        return redirect('index')
 
    return render(request, 'login.html')
 
 
def about_view(request):
    return render(request, 'about.html')
 
 
# 1. لوحة تحكم الأدمن (تم تعديل added_by إلى owner)
@login_required
def admin_dashboard_view(request):
    print("METHOD =", request.method)

    if request.method == "POST":
        print("POST DATA =", request.POST)
        print("FILES =", request.FILES)

    user_pets = Pet.objects.filter(owner=request.user).order_by('-id')
    if not request.user.is_staff and hasattr(request.user, 'profile') and request.user.profile.user_type != 'shelter':
        return redirect('index')
 
    pets = Pet.objects.filter(owner=request.user)
    incoming_requests = AdoptionRequest.objects.filter(
        pet__owner=request.user
    ).order_by('-created_at')
 
    context = {
        'pets': pets,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'dashboard.html', context)
 
 
# 3. قبول أو رفض الطلب
@login_required
def update_request_status(request, request_id, action):
    adoption_req = get_object_or_404(AdoptionRequest, id=request_id)
 
    if action == 'Approved':
        adoption_req.status = 'Approved'
        adoption_req.pet.status = 'Adopted'
        adoption_req.pet.save()
    elif action == 'Rejected':
        adoption_req.status = 'Rejected'
 
    adoption_req.save()
    return redirect('dashboard')
 
 
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')
 
 
@login_required
def dashboard_view(request):

    user_pets = Pet.objects.filter(owner=request.user).order_by('-id')
    
    # ==========================
    # Pagination for My Pets
    # ==========================
    paginator = Paginator(user_pets, 6) # تقسيم الحيوانات بحيث كل صفحة تحتوي على 6
    page_number = request.GET.get('page')
    pets_page_obj = paginator.get_page(page_number)

    total_pets = user_pets.count()
    incoming_requests = AdoptionRequest.objects.filter(
        pet__owner=request.user
    ).order_by('-created_at')
    active_requests_count = incoming_requests.filter(
        status='Pending'
    ).count()
    approved_requests_count = incoming_requests.filter(
        status='Approved'
    ).count()
    recent_requests = incoming_requests[:4]
    
    # ==========================
    # Add New Pet
    # ==========================
    if request.method == "POST":

        print("POST DATA =", request.POST)
        print("FILES =", request.FILES)

        name = request.POST.get('name')
        species = request.POST.get('species')
        breed = request.POST.get('breed')
        age = request.POST.get('age')
        location = request.POST.get('location')
        status = request.POST.get('status', 'Available')

        if name and species:
            new_pet = Pet.objects.create(
                name=name,
                species=species,
                breed=breed,
                age=age,
                location=location,
                status=status,
                owner=request.user
            )
            print("Pet Created ID:", new_pet.id)
            images = request.FILES.getlist('images')
            for img in images:
                PetImage.objects.create(
                    pet=new_pet,
                    image=img
                )
            messages.success(
                request,
                "Pet added successfully!"
            )
            return redirect('dashboard')

    context = {
        'total_pets': total_pets,
        'active_requests_count': active_requests_count,
        'approved_requests_count': approved_requests_count,
        'pets': pets_page_obj, # تم تمرير كائن الصفحة هنا بدلاً من القائمة العادية
        'recent_requests': recent_requests,
        'incoming_requests': incoming_requests,
    }
    return render(
        request,
        'dashboard.html',
        context
    )



@login_required
def my_pets_view(request):

    pets = Pet.objects.filter(
        owner=request.user
    ).order_by('-id')
    context = {
        'pets': pets,
    }
    return render(
        request,
        'dashboard.html',
        context
    )
 
 
@login_required
def delete_pet_view(request, pet_id):
    # تم تعديل added_by إلى owner
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        pet.delete()
    return redirect('dashboard')
 
def browse_pets_view(request):
    # جلب الحيوانات المتاحة
    pets_list = Pet.objects.filter(status="Available").prefetch_related("images").order_by('-id')
    
    species_query = request.GET.get('species')
    if species_query:
        pets_list = pets_list.filter(species__iexact=species_query)

    # تقسيم النتائج: 8 حيوانات في كل صفحة
    paginator = Paginator(pets_list, 8)
    page_number = request.GET.get('page')
    pets = paginator.get_page(page_number)

    context = {
        "pets": pets,
        "selected_species": species_query,
    }

    return render(request, "browse_pets.html", context)

def pet_detail_view(request, pet_id):
    # جلب الحيوان أو إظهار صفحة 404 إذا لم يتم العثور عليه
    pet = get_object_or_404(Pet.objects.prefetch_related('images'), id=pet_id)
    
    context = {
        'pet': pet,
    }
    return render(request, 'pet_detail.html', context)    

def adopt_pet_view(request, pet_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    pet = get_object_or_404(Pet, id=pet_id)
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        
        # التحقق مما إذا كان المستخدم قد قدم طلباً مسبقاً لنفس الحيوان
        if AdoptionRequest.objects.filter(pet=pet, adopter=request.user).exists():
            messages.warning(request, "You have already submitted a request for this pet.")
        else:
            # استخدام adopter بدلاً من user لأنها المعرّفة في مودلك
            AdoptionRequest.objects.create(
                pet=pet,
                adopter=request.user,
                message=message_text
            )
            messages.success(request, f"Your adoption request for {pet.name} has been sent successfully!")
            
    return redirect('pet_detail', pet_id=pet.id)

@login_required
def my_requests_view(request):
    # تم تغيير user=request.user إلى adopter=request.user بناءً على نموذج قاعدة البيانات لديك
    my_requests = AdoptionRequest.objects.filter(adopter=request.user).order_by('-created_at')
    
    pending_requests_count = my_requests.filter(status='Pending').count()
    approved_requests_count = my_requests.filter(status='Approved').count()
    rejected_requests_count = my_requests.filter(status='Rejected').count()

    context = {
        'my_requests': my_requests,
        'pending_requests_count': pending_requests_count,
        'approved_requests_count': approved_requests_count,
        'rejected_requests_count': rejected_requests_count,
    }
    return render(request, 'my_requests.html', context)   