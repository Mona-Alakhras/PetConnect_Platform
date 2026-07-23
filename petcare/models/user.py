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
    
    def register_user(self, post_data):
       
        phone_num = post_data.get('phone', None) if post_data.get('phone', '') != '' else None
        
        user =  self.model(
            username=post_data['username'],
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
            email=post_data['email'],
            phone=phone_num,
            role=post_data['role']
        )
        user.set_password(post_data['password'])
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Fallback system support for creating administrative root managers from Terminal.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Owner')

        # Use Django's native helper method for creating administrative superusers safely
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password) # Standard Django hash for administrative backends
        user.save(using=self._db)
        return user


class User(AbstractUser):
    ACCOUNT_TYPE = (
        ('Adopter', 'Adopter'),
        ('Owner', 'Owner'),
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True) 
    role = models.CharField(max_length=20, choices=ACCOUNT_TYPE, default='Adopter')

    objects = UserManager()



    class Meta:
        app_label = 'petcare'


    def __str__(self):
        return f"{self.username} ({self.role})"