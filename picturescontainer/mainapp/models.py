from django.db import models
from django.contrib.auth.models import User

class Directory(models.Model):
    name = models.CharField(max_length=200)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

class AllowedToDirectory(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_add = models.BooleanField(default=False)

def when_upload_file(instance, filename):
    return '{0}/{1}/{2}'.format(instance.directory.creator.username, instance.directory.name, filename)

class Picture(models.Model):
    name = models.CharField(max_length=200)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    picture = models.FileField(upload_to=when_upload_file)





