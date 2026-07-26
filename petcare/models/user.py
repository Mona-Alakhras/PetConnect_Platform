import re
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
 
class UserManager(BaseUserManager):
    def register_validator(self, post_data):
        """
        Handles all server-side validation for user registration.
        Validates names, email uniqueness, phone format, and role matching.
        """
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$')
       
        # Name validation
        if len(post_data.get('first_name', '')) < 2 or not post_data.get('first_name', '').isalpha():
            errors['first_name'] = "First name must be at least 2 characters long and contain letters only."
           
        if len(post_data.get('last_name', '')) < 2 or not post_data.get('last_name', '').isalpha():
            errors['last_name'] = "Last name must be at least 2 characters long and contain letters only."
           
        # Username validation (Required for Django AbstractUser compatibility)
        username = post_data.get('username', '')
        if len(username) < 3:
            errors['username'] = "Username must be at least 3 characters long."
        elif self.filter(username=username).exists():
            errors['username'] = "This username is already taken."
 
        # Email validation
        email = post_data.get('email', '')
        if not EMAIL_REGEX.match(email):
            errors['email'] = "Invalid email address format."
        elif self.filter(email=email).exists():
            errors['email'] = "This email address is already registered."
 
        # Phone validation (Optional but must be numbers if provided)
        phone = post_data.get('phone', '')
        if phone and (not phone.isdigit() or len(phone) < 7):
            errors['phone'] = "Phone number must contain digits only and be at least 7 characters long."
 
        # Password validation
        password = post_data.get('password', '')
        if len(password) < 8:
            errors['password'] = "Password must be at least 8 characters long."
        if password != post_data.get('confirm_password', ''):
            errors['confirm_password'] = "Passwords do not match."
 
        role = post_data.get('role', '')
 
        if role not in ['Adopter', 'Owner']:
            errors['role'] = "Please select a valid account type."    
           
        return errors
   
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Canonical creation path used by Django, the shell, and the test suite.
        Everything else in this manager funnels through it.
        """
        if not username:
            raise ValueError("Users must have a username.")
        if not email:
            raise ValueError("Users must have an email address.")
 
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
 
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def register_user(self, post_data):
        """Create an account from validated registration POST data."""
        phone = post_data.get('phone', '').strip() or None
 
        return self.create_user(
            username=post_data['username'],
            email=post_data['email'],
            password=post_data['password'],
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
            phone=phone,
            role=post_data['role'],
        )
 
    def create_superuser(self, username, email, password, **extra_fields):
        """Used by `manage.py createsuperuser`."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Owner')
 
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
 
        return self.create_user(username, email, password, **extra_fields)
 
 
class User(AbstractUser):
    ACCOUNT_TYPE = (
        ('Adopter', 'Adopter'),
        ('Owner', 'Owner'),
    )
 
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ACCOUNT_TYPE, default='Adopter')
 
    objects = UserManager()
 
    # `manage.py createsuperuser` prompts for these in addition to USERNAME_FIELD.
    REQUIRED_FIELDS = ['email']
 
    class Meta:
        app_label = 'petcare'
        ordering = ['-date_joined']
 
    def __str__(self):
        return f"{self.username} ({self.role})"
 
    @property
    def is_owner(self):
        return self.role == 'Owner'
 
    @property
    def is_adopter(self):
        return self.role == 'Adopter'