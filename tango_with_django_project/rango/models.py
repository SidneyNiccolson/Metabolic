from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#create the categories data model
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    #edited for the exercises at two new fields
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name
    #create the page data model
class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

class UserProfile(models.Model):
    #link user profile to a user model instance
    user = models.OneToOneField(User)

    #Additional attributes we wish to incluce
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __unicode__(self):
        return self.user.username