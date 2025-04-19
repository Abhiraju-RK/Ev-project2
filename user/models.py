from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15)

    def __str__(self):
        return self.user.username
    
