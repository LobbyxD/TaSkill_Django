from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.views.generic import ListView

from accounts.models import User_Request, UserProfile

from .forms import (Board_Creation, Give_Board_Permission,
                    Give_Organization_Permission, Organization_Creation,
                    Task_change_status, Task_Creation, Task_edit_users,
                    Task_make_progress)
from .models import (Board, Board_Permission, Organization,
                     Organization_Permission, Task, Task_status,
                     Task_status_link)

##########################
#### SIMPLE FUNCTIONS ####
##########################

def profile_fixer(user: User) -> User | None:
    """
    Checks and fixes User instance that doesn't have UserProfile instance
    Parameters
    ----------
        user: User
            User instance
    """
    try:
        if not user.profile.first_name:
            return None
        elif not user.profile.last_name:
            return None
        else:
            if user.profile.first_name:
                return user
            else:
                return user
    except:
        if user.is_authenticated:
            UserProfile.objects.create(user=user)
            if not user.profile.first_name:
                return None
            elif not user.profile.last_name:
                return None
            else:
                if user.profile.first_name:
                    return user
                else:
                    return user
        else:
            return None

def check_staff_or_permission(user: User) -> Board_Permission | Organization_Permission | None:
    """
    Checks if User instance is_staff or has Board_Permission ('owner') or Organization_Permission ('owner')
    Parameters
    ----------
        user: User
            User Instance
    """
    organization_perms = Organization_Permission.objects.filter(user=user, permissions='owner')
    board_perms = Board_Permission.objects.filter(user=user, permissions='owner')
    if user.is_staff:
        return user
    if organization_perms:
        return organization_perms
    elif board_perms:
        return board_perms
    else:
        return None

def check_edit_permissions(user: User) -> Board_Permission | Organization_Permission | None:
    """
    Checks if User instance is_staff or has Board_Permission ('owner', 'change_status', 'tasks_edit') or Organization_Permission ('owner', 'boards_edit')
    Parameters
    ----------
        user: User
            User Instance
    """
    board_edit_perms = Board_Permission.objects.filter(
        Q(user=user) &
        (Q(permissions='owner') | Q(permissions='change_status') | Q(permissions='tasks_edit'))
        )
    organization_edit_perms = Organization_Permission.objects.filter(
        Q(user=user) &
        (Q(permissions='owner') | Q(permissions='boards_edit'))
        )
    if user.is_staff:
        return user
    if organization_edit_perms:
        return organization_edit_perms
    elif board_edit_perms:
        return board_edit_perms
    else:
        return None

def check_staff_or_edit_tasks(user: User) -> Board_Permission | Organization_Permission | None:
    """
    Checks if User instance is_staff or has Board_Permission ('owner', 'tasks_edit', 'board_view') or Organization_Permission ('owner', 'boards_edit', 'boards_view')
    Parameters
    ----------
        user: User
            User Instance
    """
    board_edit_perms = Board_Permission.objects.filter(
        Q(user=user) &
        (Q(permissions='owner') | Q(permissions='tasks_edit') | Q(permissions='board_view'))
        )
    organization_edit_perms = Organization_Permission.objects.filter(
        Q(user=user) &
        (Q(permissions='owner') | Q(permissions='boards_edit') | Q(permissions='boards_view'))
        )
    if user.is_staff:
        return user
    if organization_edit_perms:
        return organization_edit_perms
    elif board_edit_perms:
        return board_edit_perms
    else:
        return None

###########################
# Create your views here. #
###########################

@login_required(login_url='login')
@user_passes_test(profile_fixer, login_url='profile_edit')  
def homepage(request) -> HttpResponse:
    """
    View page of home
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id = request.user.id)
    if not user.email:
        return redirect('profile_edit_email')

    requests = User_Request.objects.filter(to_user = user).count()
    if user.profile.organization:
        organization = user.profile.organization
    else:
        organization = Organization.objects.filter(owner=user)
    context = {
        'requests': requests,
        'organization': organization,
        }
    return render(request, 'homepage.html', context)

#------------------#
#-- Organization --#
#------------------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def organization_detail(request, slug: str) -> HttpResponse:
    """
    Organization's Detail page
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """
    organization = Organization.objects.get(slug=slug)

    user = get_object_or_404(User, id = request.user.id)
    organization_staff = Organization_Permission.objects.filter(
        organization_id = organization.id, permissions='owner', user=user
        ) 
    
    users = UserProfile.objects.filter(organization=organization)
    organization_requests = User_Request.objects.filter(
        ((Q(from_user = user) & Q(to_user = organization.owner)) | (Q(from_user=organization.owner) & Q(to_user= user)))
         & Q(type_request = 'join organization'))

    if user.profile.organization:
        check_working = True
    else:
        check_working = False
    
    if organization_staff:
        check_user_organ_staff = True
    else:
        check_user_organ_staff = False

    context = {
        'organization': organization,
        'check_working': check_working,
        'users': users,
        'organization_requests': organization_requests,
        'check_user_organ_staff': check_user_organ_staff,
    }

    return render(request,'organization_detail.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def user_organization_list(request) -> HttpResponse:
    """
    Page that shows all Organization instances created by User instance
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id = request.user.id)
    organizations = Organization.objects.filter(owner=user)
    if not organizations:
        if user.profile.organization:
            organizations = [user.profile.organization]
    context = {'organizations': organizations}
    return render(request, 'organization_list.html', context)

class All_Organizations(LoginRequiredMixin, ListView):
    """
    Page that shows ALL Organization instances
    Attributes
    ----------
        model: Organization
            the type of the model linked to the view.
        template_name: str
            the name of the html linked to the view.
        context_object_name: str
            the name for usage in the template page.
    """

    model = Organization
    template_name = 'organization_list.html'
    context_object_name = 'organizations'

@user_passes_test(check_staff_or_permission, login_url='homepage')
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def organization_edit_page(request, slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    Edit page of a specific Organization instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """
    organization = get_object_or_404(Organization, slug=slug)
    current_user_perm = Organization_Permission.objects.filter(user=request.user, permissions = 'owner')
    if not request.user.is_staff:
        if not current_user_perm:
            messages.add_message(request, messages.INFO, 'You are not one of the staff members.')
            return redirect('organization_detail', organization.slug)

    context = {
        'organization': organization,
    }

    return render(request, 'organization_edit_page.html', context)

@user_passes_test(check_staff_or_permission, login_url='homepage')
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def list_users_in_organization(request, slug: str) -> HttpResponse:
    """
    Page that lists all User instances in a specific Organization instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """

    organization = get_object_or_404(Organization, slug=slug)
        
    users = UserProfile.objects.filter(organization = organization).order_by('first_name')
    context = {
        'users': users,
    }
    request.session['organization_id'] = organization.id #FIXME if there is time organization slug not through session, like boards.

    return render(request, 'organization_user_list.html', context)

    

@user_passes_test(check_staff_or_permission, login_url='homepage')
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def view_user_organization_permissions(request, user_id: int) -> HttpResponse | HttpResponseRedirect:
    """
    Page that lists all Organization_Permission instances of a specific User instance
    Parameters
    ----------
        request: request
            session request
        user_id: int
            User Instance's ID
    """
    organization = get_object_or_404(Organization, id = request.session['organization_id'])
    current_user_perm = Organization_Permission.objects.filter(user=request.user, permissions = 'owner')
    if not request.user.is_staff:
        if not current_user_perm:
            messages.add_message(request, messages.INFO, 'You are not one of the staff members.')
            return redirect('organization_detail', organization.slug)

    user = get_object_or_404(User, id = user_id)
    user_perms = Organization_Permission.objects.filter(user = user)    
    context = {
        'organization_user': user,
        'permissions': user_perms,
        'organization': organization,
    }

    request.session['organization_id'] = organization.id
    request.session['user_id'] = user.id

    return render(request, 'organization_user_permissions.html', context)

@user_passes_test(check_staff_or_permission, login_url='homepage')
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def remove_organization_permission(request, slug: str, permission: str) -> HttpResponseRedirect:
    """
    Function that deletes a specific Organization_Permission of a specific User instance in a specific Organization instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
        permission: str
            Type of permission that is going to be removed/deleted from user
    """
    user = get_object_or_404(User, id = request.session['user_id'])
    organization = get_object_or_404(Organization, slug = slug)
    user_perm = get_object_or_404(Organization_Permission, user=user, organization=organization, permissions=permission)
    user_perm.delete()

    return redirect('view_user_organization_permissions', user.id)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def send_organization_request(request, slug: str) -> HttpResponseRedirect:
    """
    Functions that creates a User_Request instance <type_request: join_organization> from current user to Organization instance owner.
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """

    from_user = get_object_or_404(User, id = request.user.id)
    if from_user.profile.organization:
        messages.add_message(request, messages.INFO, "You're already a part of an organization.")
        return redirect('organization_detail', from_user.profile.organization.slug)
    organization = get_object_or_404(Organization, slug= slug)
    organization_request, created = User_Request.objects.get_or_create(
        from_user= from_user,
        to_user = organization.owner,
        organization=organization,
        type_request='join organization'
        )
    if created:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def leave_organization(request, slug: str) -> HttpResponseRedirect:
    """
    Function that unlinks current user from Organization instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """
    organization = get_object_or_404(Organization, slug= slug)
    user = get_object_or_404(User, id=request.user.id)
    if user.id == organization.owner.id:
        messages.add_message(request, messages.INFO, "You're the owner, you can't leave, only delete.")
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        user.profile.organization = None
        user.profile.save()
        return redirect(request.META.get('HTTP_REFERER'))

@user_passes_test(check_staff_or_permission, login_url='homepage')
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def remove_user_from_organization(request, profile_id: int) -> HttpResponseRedirect:
    """
    Function that unlinks a specific User instance from that Organization instance
    Parameters
    ----------
        request: request
            session request
        profile_id: str
            UserProfile Instance's ID
    """
    profile = get_object_or_404(UserProfile, id = profile_id)
    organization_perms = Organization_Permission.objects.filter(user = profile.user)
    board_perms = Board_Permission.objects.filter(user = profile.user)
    profile.organization = None
    organization_perms.delete()
    board_perms.delete()
    profile.save()
    return redirect(request.META.get('HTTP_REFERER'))
        
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def delete_organization(request, slug: str) -> HttpResponseRedirect:
    """
    Function that deletes Organization instance COMPLETELY (Only Organization owner or superuser can delete.)
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """
    organization = get_object_or_404(Organization, slug= slug)
    user = get_object_or_404(User, id=request.user.id)
    if organization.owner == user or user.is_staff:
        organization.delete()
        return redirect('homepage')
    else:
        messages.add_message(request, messages.INFO, "You're not the owner.")
        return redirect(request.META.get('HTTP_REFERER'))

#-----------#
#-- Board --#
#-----------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def view_boards(request) -> HttpResponse | HttpResponseRedirect:
    """
    Page that lists all Board instance of the current user, or if superuser shows ALL boards of ALL organizations
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id=request.user.id)
    user_board_perms = user.board_user_permissions.filter(Q(permissions='board_view') | Q(permissions='owner'))
    user_organ_perms = user.organization_user_permissions.filter(Q(permissions='boards_view') | Q(permissions='owner'))
    board_ids = user_board_perms.values_list('board_id', flat=True).order_by('board_id')
    if not user.is_staff:
        if not user.profile.organization:
            messages.add_message(request, messages.INFO, "You are not part of an organization.")
            return redirect('homepage')
        elif not user_board_perms:
            if not user_organ_perms:
                messages.add_message(request, messages.INFO, "You don't have the board permission.")
                return redirect('homepage')
        
    if user.is_staff:
        boards = Board.objects.all().order_by('id', 'organization')
        organization = False
    elif user_organ_perms:
        boards = Board.objects.filter(organization = user.profile.organization).order_by('id')
        try:
            organization = get_object_or_404(Organization, id = user.profile.organization.id)
        except:
            organization = False
    elif board_ids:
        boards = Board.objects.filter(id__in = board_ids).order_by('id')
        organization = get_object_or_404(Organization, id = boards.first().organization_id)
    else:
        boards = []
        organization = False

    context = {
        'boards': boards,
        'organization': organization,
    }

    return render(request, 'board_list.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_edit_permissions, login_url='view_boards')
@login_required(login_url='login')
def board_edit_page(request, slug: str) -> HttpResponse:
    """
    Edit Page of a specific Board instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug=slug)
    context = {
        'board': board,
    }
    request.session['board_id'] = board.id

    return render(request, 'board_edit_page.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def list_users_in_board(request, slug: str) -> HttpResponse:
    """
    Page that lists all User instances that are linked to a specific Board instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug = slug)
        
    users = UserProfile.objects.filter(
        id__in = Subquery(
                UserProfile.objects.filter(
                user__board_user_permissions__board_id = board.id
                ).distinct('id').values('id')
                )
            ).order_by('first_name')
    context = {
        'users': users,
        'board': board,
    }
    request.session['board_id'] = board.id

    return render(request, 'board_user_list.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def view_user_board_permissions(request, user_id: int) -> HttpResponse:
    """
    Page that lists all Board_Permission instances of a specific user
    Parameters
    ----------
        request: request
            session request
        user_id: str
            User Instance's ID
    """
    board = get_object_or_404(Board, id = request.session['board_id']) #FIXME if there is time no session, slug in link.
    user = get_object_or_404(User, id = user_id)
    user_perms = Board_Permission.objects.filter(user = user)    
    context = {
        'board_user': user,
        'permissions': user_perms,
        'board': board,
    }

    request.session['board_id'] = board.id
    request.session['user_id'] = user.id

    return render(request, 'board_user_permissions.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def remove_board_permission(request, slug: str, permission: str) -> HttpResponseRedirect:
    """
    Function that deletes a specific Board_Permission instance of a specific User in a specific Board
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
        permission: str
            The permission type that is going to be removed/deleted from user.
    """
    user = get_object_or_404(User, id = request.session['user_id']) #FIXME if there is time no session, slug in link.
    board = get_object_or_404(Board, slug = slug)
    user_perm = get_object_or_404(Board_Permission, user=user, board=board, permissions=permission)
    if user_perm:
        user_perm.delete()

    return redirect('view_user_board_permissions', user.id)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def delete_board(request, slug: str) -> HttpResponseRedirect:
    """
    Function that deletes a specific Board instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug= slug)
    board_perms = Board_Permission.objects.filter(board = board)
    board_perms.delete()
    board.delete()
    return redirect('view_boards')

#----------#
#-- Task --#
#----------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_edit_tasks, login_url='homepage') 
@login_required(login_url='login')
def view_user_tasks(request, slug: str) -> HttpResponse:
    """
    Page that lists all Task instances of a current user
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug=slug)
    board_tasks = Task.objects.filter(board = board)
    user_tasks = Task.objects.filter(Q(board = board) & Q(assignee = request.user)).exclude(status__current_status__name = 'Completed')
    context = {
        'board_tasks': board_tasks,
        'user_tasks': user_tasks,
        'board': board,
    }
    return render(request, 'tasks.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_edit_tasks, login_url='homepage') 
@login_required(login_url='login')
def task_detail(request, board_slug: str, task_slug: str) -> HttpResponse:
    """
    Page that details about specific Taks instance in a specific Board instace
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug = task_slug)
    context = {
        'board':board,
        'task': task,
    }
    return render(request, 'task_detail.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_edit_tasks, login_url='homepage')
@login_required(login_url='login')
def task_edit_page(request, board_slug: str, task_slug: str) -> HttpResponse:
    """
    Edit page of a specific Task instance in a specific Board instance
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug= task_slug)
    context = {
        'board': board,
        'task': task,
    }
    return render(request, 'task_edit_page.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def delete_task(request, board_slug: str, task_slug: str) -> HttpResponseRedirect:
    """
    Function that deletes a specific Task instance in a specific Board instance
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug = task_slug)
    task.delete()

    return redirect('view_user_tasks', board.slug)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_edit_permissions, login_url='homepage')
@login_required(login_url='login')
def send_task_to_review(request, board_slug: str, task_slug: str) -> HttpResponseRedirect:
    """
    Function that changes Task instance status to 'Review' Task_status_link instance
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug = task_slug)
    next_status = Task_status.objects.get(name = 'Review')
    task.status = Task_status_link.objects.get(current_status = next_status)
    task.save()

    return redirect('view_user_tasks', board.slug)

##################
### Form Views ###
##################

#------------------#
#-- Organization --#
#------------------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def organization_form(request) -> HttpResponse | HttpResponseRedirect:
    """
    A form to create an Organization instance.
    Also creates Organization_Permission as 'owner' to the current user
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id=request.user.id)
    form = Organization_Creation(request.POST or None, user=user)
    context = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            organ = form.save(commit=False)
            if user.is_staff:
                organ.owner = User.objects.get(id= form.cleaned_data['owner'].id)
                organ.save()
            else:
                organ.owner = user
                user.profile.organization = organ
                organ.save()
                user.profile.save()
                Organization_Permission.objects.create(organization=organ, user=user, permissions='owner')

            return redirect('organization_detail', organ.slug)
    
    return render(request, 'organization_creation.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def give_organization_permission(request, slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that create a Organization_Permission instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Organization Instance's slug
    """
    organization = get_object_or_404(Organization, slug = slug)

    form = Give_Organization_Permission(request.POST or None, user = request.user, organization = organization)
    context = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            filled_form = form.save(commit=False)
            user = filled_form.user
            permission = filled_form.permissions
            Organization_Permission.objects.create(
                user_id=user.id,
                organization_id=organization.id,
                permissions=permission
                )
            return redirect('organization_edit_page',organization.slug)
        
    return render(request, 'organization_give_permission.html', context)

#-----------#
#-- Board --#
#-----------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_edit_permissions, login_url='homepage')
@login_required(login_url='login')
def board_form(request) -> HttpResponse | HttpResponseRedirect:
    """
    A form that creates a Board instance.
    Also creates a Board_Permission instances typed 'owner' to the current user
    Parameters
    ----------
        request: request
            session request
    """
    form = Board_Creation(request.POST or None, user= request.user)
    context = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            board = form.save()
            permissions = Board_Permission.objects.create(board=board, user = request.user, permissions = 'owner')
            permissions.save()
            return redirect('view_boards')
        
    return render(request, 'board_creation.html', context)


@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_permission, login_url='homepage')
@login_required(login_url='login')
def give_board_permission(request, slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that creates a Board_Permission instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug=slug)
    
    form = Give_Board_Permission(request.POST or None, user= request.user, board= board)
    context = {'form':form}

    if request.method == 'POST':
        if form.is_valid():
            permission = form.save()
            if permission.permissions == 'tasks_edit':
                Board_Permission.objects.get_or_create(board = permission.board, user = permission.user, permissions = 'board_view')
            return redirect('board_edit_page', board.slug)
    
    return render(request, 'board_give_permission.html', context)

#----------#
#-- Task --#
#----------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_edit_permissions, login_url='homepage')
@login_required(login_url='login')
def task_form(request, slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that creates a Task instance
    Parameters
    ----------
        request: request
            session request
        slug: str
            Board Instance's slug
    """
    board = get_object_or_404(Board, slug=slug)
    form = Task_Creation(request.POST or None, user= request.user, board= board)
    context = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            task = form.save()
            return redirect('view_user_tasks', board.slug)
        
    return render(request, 'task_creation.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_edit_tasks, login_url='homepage')
@login_required(login_url='login')
def edit_assignees_to_task(request, board_slug: str, task_slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that changes Task instance's assignees (Binds and unbinds)
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug= task_slug)
    user = get_object_or_404(User, id = request.user.id)
    form = Task_edit_users(request.POST or None, instance=task, board=board, user=user)
    context = {
        'form': form,
    }
    
    if request.method == 'POST':
        if form.is_valid:
            form.save()

            return redirect('task_detail', board.slug, task.slug)

    return render(request, 'task_creation.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_staff_or_edit_tasks, login_url='homepage')
@login_required(login_url='login')
def task_make_progress(request, board_slug: str, task_slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that changes Task instance's assignee_progress.
    Also changes "Open" status to "In-Progress"
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug = task_slug)
    form = Task_make_progress(request.POST or None, instance=task)

    if request.method == 'POST':
        if form.is_valid():
            if task.status.current_status.name == 'Open':
                next_status = task.status.next_statuses.get(name='In-Progress')
                task.status = Task_status_link.objects.get(current_status = next_status)
                task.save()
            form.save()
            return redirect('task_detail', board.slug, task.slug)

    context = {
        'board': board,
        'task': task,
        'form': form,
    }
    
    return render(request, 'task_make_progress.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@user_passes_test(check_edit_permissions, login_url='homepage')
@login_required(login_url='login')
def change_task_status(request, board_slug: str, task_slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    A form that changes Task instance's status
    Parameters
    ----------
        request: request
            session request
        board_slug: str
            Board Instance's slug
        task_slug: str
            Task Instance's slug
    """
    board = get_object_or_404(Board, slug = board_slug)
    task = get_object_or_404(Task, slug = task_slug)
    form = Task_change_status(request.POST or None, instance=task, user = request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('task_detail', board.slug, task.slug)

    context = {
        'board': board,
        'task': task,
        'form': form
    }

    return render(request, 'task_change_status.html', context)

####################
### Search Views ###
####################

#------------------#
#-- Organization --#
#------------------#

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def organization_search(request) -> HttpResponse:
    """
    View that lists all organization that contains a specific search value.
    Parameters
    ----------
        request: request
            session request
    """
    query_dict = request.GET
    user = get_object_or_404(User, id = request.user.id)
    q = query_dict.get('q')
    if q is not None:
            organizations = Organization.objects.filter(name__icontains=q).exclude(owner=user)
    else:
        organizations = Organization.objects.all()
    
    context = {'organizations': organizations}
    return render(request, 'organization_list.html', context)