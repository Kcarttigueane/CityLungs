from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.CITIZEN)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier."""
    
    # Role choices
    CITIZEN = 'citizen'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (CITIZEN, _('Citizen')),
        (ADMIN, _('Administrator')),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CITIZEN,
        help_text=_('Designates the user role.'),
    )
    
    # Additional user profile fields
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    address = models.CharField(_('address'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('last login'), auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    
    def is_admin(self):
        """Check if the user is an administrator."""
        return self.role == self.ADMIN
    
    def is_citizen(self):
        """Check if the user is a citizen."""
        return self.role == self.CITIZEN


class UserProfile(models.Model):
    """
    Extended User Profile for storing additional user preferences and settings.
    This model can be extended with project-specific fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    # User preferences for dashboard
    default_view = models.CharField(max_length=50, default='pollution')  # e.g., 'pollution', 'traffic', 'weather'
    notification_threshold = models.IntegerField(default=75)  # Threshold for alerts (e.g., pollution level)
    
    def __str__(self):
        return f"Profile for {self.user.email}"