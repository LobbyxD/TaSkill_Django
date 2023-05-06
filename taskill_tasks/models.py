from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.urls import reverse

##################
### Validators ###
##################


# Create your models here.

class Task_status(models.Model):
    """
    Task_status Model, saves the name of the status.
    Attributes
    ----------
        name: str
            The name of the status, max characters - 50. unique & pk (True)
    """

    name = models.CharField(max_length = 50, primary_key=True ,unique=True)

    def __str__(self) -> str:
        return f'{self.name}'


class Task_status_link(models.Model):
    """
    Task_status_link Model, links between Task_status instances.
    Attributes
    ----------
        current_status: Task_status Instance
            Task_status Instance
        next_statuses: Task_status Instances
            Task_status Instances
    """
    current_status = models.OneToOneField(Task_status, on_delete=models.CASCADE, related_name='task_status')
    next_statuses = models.ManyToManyField(Task_status, related_name = 'next_statuses')

    def __str__(self) -> str:
        return f'{self.current_status.name}'
     

class Organization(models.Model):
    """
    Organization Model, saves organization's data
    Attributes
    ----------
        name: str
            Organization's name, max length 50 characters, unique.
        owner: User Instance
            User Instances, One to one.
        slug: str
            Organization's slug name(leave blank to auto-create)
    """

    name = models.CharField(max_length = 50, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='organization_owner')
    slug = models.SlugField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("organization_detail", args=[self.slug])

class Organization_Permission(models.Model):
    """
    Organization_Permission Model, saves organization's permissions
    Attributes
    ----------
        organization: Organization Instance
            Organization instance link.
        user: User Instance
            User Instances, One to one.
        permissions: str
            Type of permission you want to give the user.

        PERMISSIONS: str
            holds the different permission choices.
        PERMISSIONS_AND_EMPTY: str
            holds the different permission choices + empty label.
    """

    PERMISSIONS = [
        ('owner', 'Owner'),
        ('boards_view', 'View Boards'),
        ('boards_edit', 'Edit Boards'),
        ]
    
    PERMISSIONS_AND_EMPTY = [('','Select Permission')] + PERMISSIONS

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_user_permissions')
    permissions = models.CharField(max_length=100, choices=PERMISSIONS_AND_EMPTY)

    class Meta:
        unique_together = ['organization', 'user', 'permissions']

    def __str__(self) -> str:
        return f'{self.user}: {self.permissions}'

class Board(models.Model):
    """
    Board Model, saves board's data
    Attributes
    ----------
        name: str
            Board's name, max length 50 characters
        organization: Organization Instance
            Organization instance link.
        user: User Instance
            User Instances, One to one.
        initial_task_status: Task_status_link instance
            the first Task_status_link instance, that will showen when created new Tasks.
        slug: str
            Board's slug name(leave blank to auto-create)
    """

    name = models.CharField(max_length = 50)
    organization = models.ForeignKey(Organization, on_delete= models.CASCADE)
    initial_task_status = models.ForeignKey(Task_status_link, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ['organization', 'name']

    def __str__(self) -> str:
        return self.name
        

class Board_Permission(models.Model):
    """
    Board_Permission Model, saves board's permissions
    Attributes
    ----------
        board: Board Instance
            Board instance link.
        user: User Instance
            User Instances, that will be linked to the permission.
        permissions: str
            Type of permission you want to give the user.

        PERMISSIONS: str
            holds the different permission choices.
        PERMISSIONS_AND_EMPTY: str
            holds the different permission choices + empty label.
    """

    PERMISSIONS = [
        ('owner', 'Owner'),
        ('board_view', 'View Board'),
        ('change_status', 'Change Statuses'),
        ('tasks_edit', 'Edit Tasks'),
    ]

    PERMISSIONS_AND_EMPTY = [('','Select Permission')] + PERMISSIONS

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='board_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_user_permissions')
    permissions = models.CharField(max_length=100, choices=PERMISSIONS_AND_EMPTY)

    class Meta:
        unique_together = ['board', 'user', 'permissions']

class Task(models.Model):
    """
    Task Model, saves task's data
    Attributes
    ----------
        board: Board Instance
            Board instance link.
        title: str
            The name of the task, max length 50 characters
        description: str
            The description of the task, max length 200 characters
        assignee_progress: str
            The progress of the assignees in the task, max length 200000 characters
        assignee: User Instances
            User Instances, that will be linked to the task.
        status: Task_status_link Instance
            Task_status_link Instance that the task is linked to.
        slug: str
            Task's slug name(leave blank to auto-create)
    """

    
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length = 200)
    assignee_progress = models.TextField(max_length = 200000, blank=True, null=True)
    assignee = models.ManyToManyField(User, related_name= 'task')
    status = models.ForeignKey(Task_status_link, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)

#############
# Functions #
#############

def slugify_instance(instance) -> object:
    """
    Slugifies an instance
    Parameters
    ----------
        instance: object
    """
    try:
        if instance.name:
            name_id = f'{instance.name} {instance.id}'
            slug = slugify(name_id)
            return slug
    except AttributeError:
        if instance.title:
            title_id = f'{instance.title} {instance.id}'
            slug = slugify(title_id)
            return slug

def instance_post_save(sender, instance, created, *args, **kwargs):
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

###################
# Post Save calls #
###################

post_save.connect(receiver = instance_post_save, sender=Organization)
post_save.connect(receiver = instance_post_save, sender=Board)
post_save.connect(receiver = instance_post_save, sender=Task)
