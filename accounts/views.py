from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from taskill_tasks.models import Organization
from taskill_tasks.views import profile_fixer

from .forms import ImageChangeForm, ProfileForm, SignupForm, User_Email_Form
from .models import User_Request, UserProfile

#############################
### Login/Logout/Register ###
#############################

def register(request) -> HttpResponse | HttpResponseRedirect:
    """
    Form that registers a new user in  the system and logs them in.
    Parameters
    ----------
        request: request
            session request
    """
    signup_form = SignupForm(request.POST or None)
    context = {'form': signup_form}

    if request.method == 'POST':
        if signup_form.is_valid():
            user = signup_form.save()
            u_username = signup_form.cleaned_data['username']
            u_password = signup_form.cleaned_data['password1']
            user  = authenticate(username = u_username,password = u_password)
            if user:
                login(request, user)
                return redirect('profile_edit')
            else:
                messages.add_message(request, messages.ERROR, 'User not authenticated.')
                return redirect('login')
        else:
            return render(request, 'register.html', context)

    return render(request,'register.html', context)

def user_login(request) -> HttpResponse | HttpResponseRedirect:
    """
    Form that logs the user in to the system
    Parameters
    ----------
        request: request
            session request
    """
    if request.user.is_authenticated:
        return redirect('homepage')
    
    form = AuthenticationForm(request.POST or None)

    if request.method == 'POST':
        u_username = request.POST.get('username')
        u_password = request.POST.get('password')
        user = authenticate(username = u_username, password = u_password)
        
        if user:
            login(request, user)                
            path_redirect = request.get_full_path().split('?next=',1)
            if '?next=' in request.get_full_path():
                path_redirect = path_redirect[1].replace('%3F', '?').replace('%3D','=')
                return HttpResponseRedirect(path_redirect)
            else:
                return redirect('homepage')
        else:
            messages.add_message(request, messages.WARNING, 'Username or Password are incorrect.')

    context = {'form': form}
    return render(request, 'login.html', context)

def user_logout(request) -> HttpResponseRedirect:
    """
    Function the logs the user out of the system
    Parameters
    ----------
        request: request
            session request
    """
    logout(request)
    return redirect('login')

################
### Profile ###
################

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def profile(request) -> HttpResponse | HttpResponseRedirect:
    """
    Page that shows details about current user
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id = request.user.id)
    if user.is_staff:
        return redirect('admin:index')

    profile = user.profile
    if profile.manager:
        manager_profile = UserProfile.objects.get(user = profile.manager)
    else:
        manager_profile = None
        
    context = {
        'profile': profile,
        'manager': manager_profile
        }
    
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def profile_edit(request) -> HttpResponse | HttpResponseRedirect:
    """
    Form that edits UserProfile instance's information.
    Parameters
    ----------
        request: request
            session request
    """
    profile = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile)
    context = {'form': form}

    if form.is_valid():
        form.save()
        return redirect('profile')

    return render(request, 'profile_edit.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def profile_edit_email(request) -> HttpResponse | HttpResponseRedirect:
    """
    Form that edits User instance's email
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id = request.user.id)
    if user.email:
        return redirect('homepage')
    form = User_Email_Form(request.POST or None, instance=user)
    context = {'form': form}

    if form.is_valid():
        form.save()
        return redirect('profile')

    return render(request, 'profile_edit.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def update_profile_image(request) -> HttpResponse | HttpResponseRedirect:
    """
    Form that changes UserProfile instance's image url
    Parameters
    ----------
        request: request
            session request
    """
    profile = request.user.profile
    form = ImageChangeForm(request.POST or None)
    context = {'form': form}

    if form.is_valid():
        profile.image = form.cleaned_data['image']
        profile.save()
        return redirect('profile')

    return render(request, 'profile_edit.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def find_profile(request, slug: str) -> HttpResponse | HttpResponseRedirect:
    """
    Page that shows details of a specific UserProfile instance.
    Parameters
    ----------
        request: request
            session request
        slug: str
            UserProfile Instance's slug
    """
    current_user = get_object_or_404(User, id = request.user.id)
    profile = get_object_or_404(UserProfile, slug=slug)
    profile_user = profile.user
    if not current_user.is_staff:
        if current_user.profile.slug == slug:
            return redirect('profile')
        
    if profile.manager:
        manager_profile = UserProfile.objects.get(user = profile.manager)
    else:
        manager_profile = None
    
    request.session['viewed_profile'] = profile.slug

    incommon_friend_requests = User_Request.objects.filter(
        ((Q(from_user = current_user) & Q(to_user = profile_user)) | (Q(from_user=profile_user) & Q(to_user= current_user)))
         & Q(type_request = 'friend'))
    incommon_manager_requests = User_Request.objects.filter(
        ((Q(from_user = current_user) & Q(to_user = profile_user)) | (Q(from_user=profile_user) & Q(to_user= current_user)))
         & Q(type_request = 'manager'))

    check_friendship = current_user in profile.friends.filter(id= current_user.id)

    current_manager = current_user.profile.manager
    if current_manager:
        check_manager = (profile == current_manager.profile)
    else:
        check_manager = (profile.manager == current_user)

    context = {
        'profile': profile,
        'manager': manager_profile,
        'user_friend_requests': incommon_friend_requests,
        'user_manager_requests': incommon_manager_requests,
        'check_friendship': check_friendship,
        'check_manager': check_manager,
           }

    return render(request, 'find_profile.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def profile_search(request) -> HttpResponse:
    """
    Page that shows all UserProfile instances that contains same values of the search parameter
    Parameters
    ----------
        request: request
            session request
    """
    query_dict = request.GET
    user = get_object_or_404(User, id = request.user.id)
    q = query_dict.get('q')
    if q is not None:
        profiles = UserProfile.objects.filter(
            Q(first_name__icontains = q) | Q(last_name__icontains = q)
            ).exclude(user = user)
        organizations = Organization.objects.filter(name__icontains = q).exclude(owner=user)
    else:
        profiles = UserProfile.objects.all().exclude(user = user)
        organizations = Organization.objects.all().exclude(owner=user)
    
    context = {'profiles': profiles, 'organizations': organizations}
    return render(request, 'profile_search.html', context)

####################
### User_Request ###
####################

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def send_friend_request(request, user_id: int) -> HttpResponseRedirect:
    """
    Function that creates a User_Request instance type 'friend'
    Parameters
    ----------
        request: request
            session request
        user_id: int
            User Instance's ID
    """
    from_user = get_object_or_404(User, id = request.user.id)
    to_user = User.objects.get(id=user_id)
    friend_request, created = User_Request.objects.get_or_create(from_user= from_user, to_user=to_user, type_request='friend')
    if created:
        return redirect('find_profile', to_user.profile.slug)
    else:
        return redirect('find_profile', to_user.profile.slug)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def send_manager_request(request, user_id: int) -> HttpResponseRedirect:
    """
    Function that creates a User_Request instance type 'manager'
    Parameters
    ----------
        request: request
            session request
        user_id: int
            User Instance's ID
    """
    from_user = get_object_or_404(User, id = request.user.id)
    to_user = get_object_or_404(User, id=user_id)
    manager_request, created = User_Request.objects.get_or_create(from_user= from_user, to_user=to_user, type_request='manager')
    if created:
        return redirect('find_profile', to_user.profile.slug)
    else:
        return redirect('find_profile', to_user.profile.slug)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def remove_request(request, request_id: int) -> HttpResponseRedirect:
    """
    Function the deletes User_Request instance
    Parameters
    ----------
        request: request
            session request
        request_id: int
            User_Request Instance's ID
    """
    the_request = get_object_or_404(User_Request, id=request_id)
    the_request.delete()

    return redirect(request.META.get('HTTP_REFERER'))

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def accept_request(request, request_id: int) -> HttpResponseRedirect:
    """
    Function that links User_Request instance to User/UserProfile instance and then deletes the request after 'accepting'
    Parameters
    ----------
        request: request
            session request
        request_id: int
            User_Request Instance's ID
    """
    current_profile_id = request.user.profile.id
    the_request = get_object_or_404(User_Request, id=request_id)
    if the_request.to_user == request.user and the_request.type_request == 'friend':
        the_request.to_user.friends.add(the_request.from_user.profile)
        the_request.from_user.friends.add(the_request.to_user.profile)
        the_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    elif the_request.to_user == request.user and the_request.type_request == 'manager':
        the_request.to_user.profile.manager = the_request.from_user
        the_request.to_user.profile.save()
        the_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    elif the_request.to_user == request.user and the_request.type_request == 'join organization':
        the_request.from_user.profile.organization = the_request.organization
        the_request.from_user.profile.save()
        the_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('user_requests')

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def unfriend(request, user_id: int) -> HttpResponseRedirect:
    """
    Function that unlinks UserProfile instances from each other.
    Parameters
    ----------
        request: request
            session request
        user_id: int
            User Instance's ID
    """
    current_profile = get_object_or_404(UserProfile, id=request.user.profile.id)
    friend = get_object_or_404(UserProfile, id=user_id)
    current_profile.friends.remove(friend.user)
    friend.friends.remove(current_profile.user)
    current_profile.save()
    friend.save()

    return redirect(request.META.get('HTTP_REFERER'))

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def remove_manager(request, user_id: int) -> HttpResponseRedirect:
    """
    Function the unlinks manager from UserProfile instance.
    Parameters
    ----------
        request: request
            session request
        user_id: int
            User Instance's ID
    """
    viewed_profile = get_object_or_404(UserProfile,slug = request.session.get('viewed_profile'))
    current_profile = get_object_or_404(UserProfile, user = request.user)

    if current_profile.manager.id != user_id or current_profile == None:
        return redirect('find_profile', viewed_profile.slug)
    elif viewed_profile.manager:
        if viewed_profile.manager.profile == current_profile:
            viewed_profile.manager = None
            viewed_profile.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        current_profile.manager = None
        current_profile.save()
        return redirect(request.META.get('HTTP_REFERER'))
        
@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def user_requests(request) -> HttpResponse:
    """
    Page that lists all User_Request instances of the current user
    Parameters
    ----------
        request: request
            session request
    """
    user = get_object_or_404(User, id = request.user.id)
    recieved_requests = User_Request.objects.filter(to_user=user)
    sent_requests = User_Request.objects.filter(from_user=user)
    context = {
        'recieved_requests': recieved_requests,
        'sent_requests': sent_requests,
    }

    return render(request,'user_requests.html', context)

@user_passes_test(profile_fixer, login_url='profile_edit')
@login_required(login_url='login')
def friend_list(request) -> HttpResponse:
    """
    Page that lists all UserProfile instances(friends) of the current user
    Parameters
    ----------
        request: request
            session request
    """
    friends = request.user.friends.all()
    context = {'friends': friends}

    return render(request, 'friend_list.html', context)