from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 
from django.db import models 


class UserManager(BaseUserManager): 
      def create_user(self, email, password=None): 
            if not email: 
                 raise ValueError("Users must have an email address") 
            email = self.normalize_email(email) 
            user = self.model(email=email) 
            user.set_password(password) 
            user.save(using=self._db) 
            return user 
      
      def create_superuser(self, email, password): 
        user = self.create_user(email, password) 
        user.is_admin = True 
        User.is_superuser = True 
        user.save(using=self._db) 
        return user
 
class User(AbstractBaseUser): 
    email = models.EmailField(unique=True) 
    name = models.CharField(max_length =255) 
    is_active = models.BooleanField(default=True) 
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    objects = UserManager() 
 
    USERNAME_FIELD = 'email' 


class Todolist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.CharField(max_length=255)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=[
        ('export', 'Export'),
        ('import', 'Import')
    ])
    task_count = models.IntegerField(default=0) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type} ({self.task_count} tasks)"
