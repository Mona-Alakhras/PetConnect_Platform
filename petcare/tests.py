"""Tests covering authorisation rules, adoption flow and page rendering."""
 
from django.test import TestCase
from django.urls import reverse
 
from .models import AdoptionRequest, Pet, User
 
 
def make_user(username, role='Adopter', **extra):
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='StrongPassw0rd!',
        first_name=username.capitalize(),
        last_name='Tester',
        role=role,
        **extra,
    )
 
 
class PublicPageTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner1', role='Owner')
        self.pet = Pet.objects.create(
            name='Max', species='Dog', breed='Golden Retriever',
            age='2 years', location='Gaza', owner=self.owner,
        )
 
    def test_home_page_renders(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PetConnect')
 
    def test_about_page_renders(self):
        self.assertEqual(self.client.get(reverse('about')).status_code, 200)
 
    def test_browse_shows_available_pets(self):
        response = self.client.get(reverse('browse_pets'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Max')
 
    def test_browse_species_filter_applies_server_side(self):
        Pet.objects.create(
            name='Whiskers', species='Cat', breed='Persian',
            age='1 year', location='Gaza', owner=self.owner,
        )
        response = self.client.get(reverse('browse_pets'), {'species': 'Cat'})
        self.assertContains(response, 'Whiskers')
        self.assertNotContains(response, '>Max<')
 
    def test_browse_ignores_unknown_species(self):
        response = self.client.get(reverse('browse_pets'), {'species': 'Dragon'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_species'], '')
 
    def test_pet_detail_renders(self):
        response = self.client.get(reverse('pet_detail', args=[self.pet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Golden Retriever')
 
    def test_adopted_pets_are_hidden_from_browse(self):
        self.pet.status = 'Adopted'
        self.pet.save()
        self.assertNotContains(self.client.get(reverse('browse_pets')), '>Max<')
 
 
class AuthorisationTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner1', role='Owner')
        self.other_owner = make_user('owner2', role='Owner')
        self.adopter = make_user('adopter1')
        self.pet = Pet.objects.create(
            name='Max', species='Dog', breed='Beagle',
            age='2 years', location='Gaza', owner=self.owner,
        )
 
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
 
    def test_adopter_cannot_open_owner_dashboard(self):
        self.client.force_login(self.adopter)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('index'))
 
    def test_owner_can_open_dashboard(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
 
    def test_owner_cannot_approve_another_owners_request(self):
        """The IDOR guard: knowing the request id must not be enough."""
        adoption = AdoptionRequest.objects.create(
            pet=self.pet, adopter=self.adopter, message='x' * 30,
        )
        self.client.force_login(self.other_owner)
 
        response = self.client.post(
            reverse('update_request_status', args=[adoption.id, 'Approved'])
        )
 
        self.assertEqual(response.status_code, 404)
        adoption.refresh_from_db()
        self.pet.refresh_from_db()
        self.assertEqual(adoption.status, 'Pending')
        self.assertEqual(self.pet.status, 'Available')
 
    def test_owner_can_approve_own_request(self):
        adoption = AdoptionRequest.objects.create(
            pet=self.pet, adopter=self.adopter, message='x' * 30,
        )
        self.client.force_login(self.owner)
 
        response = self.client.post(
            reverse('update_request_status', args=[adoption.id, 'Approved']),
            headers={'x-requested-with': 'XMLHttpRequest'},
        )
 
        self.assertEqual(response.status_code, 200)
        adoption.refresh_from_db()
        self.pet.refresh_from_db()
        self.assertEqual(adoption.status, 'Approved')
        self.assertEqual(self.pet.status, 'Adopted')
 
    def test_approving_rejects_the_other_pending_requests(self):
        winner = AdoptionRequest.objects.create(
            pet=self.pet, adopter=self.adopter, message='x' * 30,
        )
        runner_up = AdoptionRequest.objects.create(
            pet=self.pet, adopter=make_user('adopter2'), message='y' * 30,
        )
        self.client.force_login(self.owner)
 
        self.client.post(
            reverse('update_request_status', args=[winner.id, 'Approved']),
            headers={'x-requested-with': 'XMLHttpRequest'},
        )
 
        runner_up.refresh_from_db()
        self.assertEqual(runner_up.status, 'Rejected')
 
    def test_unknown_action_is_rejected(self):
        adoption = AdoptionRequest.objects.create(
            pet=self.pet, adopter=self.adopter, message='x' * 30,
        )
        self.client.force_login(self.owner)
 
        response = self.client.post(
            reverse('update_request_status', args=[adoption.id, 'Deleted'])
        )
 
        self.assertEqual(response.status_code, 400)
        adoption.refresh_from_db()
        self.assertEqual(adoption.status, 'Pending')
 
    def test_status_update_rejects_get(self):
        adoption = AdoptionRequest.objects.create(
            pet=self.pet, adopter=self.adopter, message='x' * 30,
        )
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse('update_request_status', args=[adoption.id, 'Approved'])
        )
        self.assertEqual(response.status_code, 405)
 
    def test_owner_cannot_delete_another_owners_pet(self):
        self.client.force_login(self.other_owner)
        response = self.client.post(reverse('delete_pet', args=[self.pet.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Pet.objects.filter(id=self.pet.id).exists())
 
    def test_owner_can_delete_own_pet(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('delete_pet', args=[self.pet.id]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Pet.objects.filter(id=self.pet.id).exists())
 
    def test_delete_rejects_get(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('delete_pet', args=[self.pet.id]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Pet.objects.filter(id=self.pet.id).exists())
 
 
class AdoptionRequestTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner1', role='Owner')
        self.adopter = make_user('adopter1')
        self.pet = Pet.objects.create(
            name='Max', species='Dog', breed='Beagle',
            age='2 years', location='Gaza', owner=self.owner,
        )
        self.url = reverse('adopt_pet', args=[self.pet.id])
        self.message = {'message': 'I have a big garden and years of experience.'}
 
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.post(self.url, self.message)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
 
    def test_adopter_can_submit_request(self):
        self.client.force_login(self.adopter)
        self.client.post(self.url, self.message)
        self.assertTrue(
            AdoptionRequest.objects.filter(pet=self.pet, adopter=self.adopter).exists()
        )
 
    def test_owner_cannot_adopt_own_pet(self):
        self.client.force_login(self.owner)
        self.client.post(self.url, self.message)
        self.assertEqual(AdoptionRequest.objects.count(), 0)
 
    def test_cannot_adopt_an_already_adopted_pet(self):
        self.pet.status = 'Adopted'
        self.pet.save()
        self.client.force_login(self.adopter)
        self.client.post(self.url, self.message)
        self.assertEqual(AdoptionRequest.objects.count(), 0)
 
    def test_short_message_is_rejected(self):
        self.client.force_login(self.adopter)
        self.client.post(self.url, {'message': 'pls'})
        self.assertEqual(AdoptionRequest.objects.count(), 0)
 
    def test_duplicate_request_is_blocked(self):
        self.client.force_login(self.adopter)
        self.client.post(self.url, self.message)
        self.client.post(self.url, self.message)
        self.assertEqual(AdoptionRequest.objects.count(), 1)
 
 
class AccountTests(TestCase):
    def test_registration_creates_user(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Sara', 'last_name': 'Ahmed',
            'username': 'sara', 'email': 'sara@example.com',
            'phone': '0599123456', 'password': 'StrongPassw0rd!',
            'confirm_password': 'StrongPassw0rd!', 'role': 'Adopter',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='sara').exists())
 
    def test_invalid_registration_keeps_submitted_values(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'S', 'last_name': 'Ahmed',
            'username': 'sara', 'email': 'not-an-email',
            'password': 'short', 'confirm_password': 'nope', 'role': 'Adopter',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="sara"')
        self.assertFalse(User.objects.filter(username='sara').exists())
 
    def test_login_and_logout(self):
        make_user('adopter1')
        response = self.client.post(reverse('login'), {
            'username': 'adopter1', 'password': 'StrongPassw0rd!',
        })
        self.assertRedirects(response, reverse('index'))
 
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
 
    def test_owner_lands_on_dashboard_after_login(self):
        make_user('owner1', role='Owner')
        response = self.client.post(reverse('login'), {
            'username': 'owner1', 'password': 'StrongPassw0rd!',
        })
        self.assertRedirects(response, reverse('dashboard'))
 
    def test_logout_rejects_get(self):
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
 
    def test_forgot_password_response_does_not_leak_accounts(self):
        make_user('adopter1')
        known = self.client.post(
            reverse('api_forgot_password'), {'email': 'adopter1@example.com'}
        ).json()
        unknown = self.client.post(
            reverse('api_forgot_password'), {'email': 'nobody@example.com'}
        ).json()
        self.assertEqual(known, unknown)
 
 
class DashboardTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner1', role='Owner')
        self.client.force_login(self.owner)
 
    def test_owner_can_add_a_pet(self):
        response = self.client.post(reverse('dashboard'), {
            'name': 'Luna', 'species': 'Cat', 'breed': 'Persian',
            'age': '1 year', 'location': 'Gaza', 'status': 'Available',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Pet.objects.filter(name='Luna', owner=self.owner).exists())
 
    def test_invalid_pet_submission_is_rejected(self):
        self.client.post(reverse('dashboard'), {
            'name': '', 'species': 'Cat', 'breed': 'Persian',
            'age': '1 year', 'location': 'Gaza',
        })
        self.assertEqual(Pet.objects.count(), 0)
 
    def test_dashboard_only_lists_own_pets(self):
        other = make_user('owner2', role='Owner')
        Pet.objects.create(
            name='NotMine', species='Dog', breed='Beagle',
            age='3 years', location='Gaza', owner=other,
        )
        mine = Pet.objects.create(
            name='Mine', species='Dog', breed='Beagle',
            age='3 years', location='Gaza', owner=self.owner,
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(list(response.context['pets']), [mine])
 
 
class IconTagTests(TestCase):
    def test_known_icon_renders_svg(self):
        from .templatetags.icons import icon
 
        markup = icon('paw')
        self.assertIn('<svg', markup)
        self.assertIn('currentColor', markup)
        self.assertIn('aria-hidden="true"', markup)
 
    def test_labelled_icon_is_exposed_to_screen_readers(self):
        from .templatetags.icons import icon
 
        markup = icon('paw', label='Pets')
        self.assertIn('role="img"', markup)
        self.assertIn('aria-label="Pets"', markup)
 
    def test_unknown_icon_renders_nothing(self):
        from .templatetags.icons import icon
 
        self.assertEqual(icon('does-not-exist'), '')
 
    def test_attributes_are_escaped(self):
        from .templatetags.icons import icon
 
        markup = icon('paw', label='<script>alert(1)</script>')
        self.assertNotIn('<script>', markup)
 
 