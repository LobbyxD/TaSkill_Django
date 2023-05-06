from country_list import countries_for_language
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.urls import reverse

from taskill_tasks.models import Organization

# MODELS

class UserProfile(models.Model):
    """
    UserProfile Model, saves User's Profile data.
    Attributes
    ----------
        COUNTRIES: str
            The country choices
        user: User Instance
            User Instance, that will be linked to the UserProfile.
        first_name: str
            The first name of the user, max length 100 characters
        last_name: str
            The last name of the user, max length 100 characters
        country: str
            Where the user is from, max length 100
        manager: User Instance
            User Instance, that will be linked to the user as manager.
        friends: User Instances
            User Instances, that will be linked to the user as friends.
        image: str
            Image URL, that will be shown as a picture at the profile page.
        slug: str
            UserProfile's slug name(leave blank to auto-create)
    """


    COUNTRIES = countries_for_language('en')

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, choices=COUNTRIES)
    manager = models.ForeignKey(User, related_name='profiles', null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, related_name='profiles',null=True, blank=True, on_delete=models.SET_NULL)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    image = models.URLField(default='https://st3.depositphotos.com/15437752/19006/i/600/depositphotos_190061104-stock-photo-silhouette-male-gradient-background-white.jpg')
    slug = models.SlugField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse("profile", args= [self.slug])

class User_Request(models.Model):
    """
    UserProfile Model, saves User's Profile data.
    Attributes
    ----------
        CHOICES: str
            The type of request choices
        from_user: User Instance
            User Instance, that will be linked to the User_Request.
        to_user: User Instance
            User Instance, that will be linked to the User_Request.
        organization: Organization Instance
            Organization Instance, that will be linked to the User_Request (not required)
        type_request: str
            Type of request, max length 100 characters.
    """
    CHOICES = [
        ('Friend','friend'),
        ('Manager', 'manager'),
        ('Join Organization', 'join organization'),
        ]
    
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE, blank=True, null=True)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE, blank=True, null=True)
    organization = models.ForeignKey(Organization, related_name='organization', on_delete=models.CASCADE, blank=True, null=True)
    type_request = models.CharField(max_length=100, choices=CHOICES)

# Functions

def slugify_instance(instance) -> object:
    """
    Slugifies an instance
    Parameters
    ----------
        instance: object
    """
    name_id = f'{instance.first_name} {instance.last_name} {instance.id}'
    slug = slugify(name_id)
    return slug

def profile_post_save(sender, instance, created, *args, **kwargs):
    """
    Saves slug into instances slug.
    Parameters
    ----------
    sender: object
        The object that activated the function
    instance: object
        The object that this function works on
    created: boolean
        Checks if it was created or not
    """
    slug = slugify_instance(instance)
    if created or not instance.slug:
        instance.slug = slug
        instance.save()
    else:
        if slug != instance.slug:
            instance.slug = slug
            instance.save()

def post_profile_group(sender, instance, created, *args, **kwargs):
    """
    Links users to default 'guest' group.
    Parameters
    ----------
    sender: object
        The object that activated the function
    instance: object
        The object that this function works on
    created: boolean
        Checks if it was created or not
    """
    if created:
        if not instance.is_staff:
            UserProfile.objects.create(user_id = instance.id)
            Group.objects.get(name= 'guest').user_set.add(instance)

post_save.connect(receiver=profile_post_save, sender=UserProfile)
post_save.connect(receiver=post_profile_group, sender=User)