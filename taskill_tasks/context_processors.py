from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse

from taskill_tasks.models import (Board, Board_Permission,
                                  Organization_Permission)

####################
### Organization ###
####################

def check_organization_staff(request) -> dict:
    """
    Function that adds 'organization_staff_perms' to context
    Parameters
    ----------
        request: request
            session request
    """
    if not request.path == reverse('login'):
        if not request.path == reverse('register'):
            user = get_object_or_404(User, id = request.user.id)
            organization_staff_perms = Organization_Permission.objects.filter(Q(user=user) & (Q(permissions='owner')))
            return {'organization_staff_perms': organization_staff_perms}
        else:
            return {}
    else:
        return {}

#############
### Board ###
#############

def check_board_lg_0(request) -> dict:
    """
    Function that adds 'organization_boards' to context
    Parameters
    ----------
        request: request
            session request
    """
    if not request.path == reverse('login'):
        if not request.path == reverse('register'):
            user = get_object_or_404(User, id = request.user.id)
            boards = Board.objects.filter(organization = user.profile.organization)
            if boards:
                return {'organization_boards':boards}
    return {}


def check_board_view(request) -> dict:
    """
    Function that adds 'board_view_perms' and 'organization_view_perms' to context
    Parameters
    ----------
        request: request
            session request
    """
    if not request.path == reverse('login'):
        if not request.path == reverse('register'):
            user = get_object_or_404(User, id = request.user.id)
            board_view_perms = Board_Permission.objects.filter(Q(user=user) & (Q(permissions='owner') | Q(permissions='board_view')))
            organization_view_perms = Organization_Permission.objects.filter(Q(user=user) & (Q(permissions='owner') | Q(permissions='boards_view')))
            return {'board_view_perms': board_view_perms, 'organization_view_perms': organization_view_perms}
        else:
            return {}
    else:
        return {}

def check_board_edit(request) -> dict:
    """
    Function that adds 'board_edit_perms' and 'organization_edit_perms' to context
    Parameters
    ----------
        request: request
            session request
    """
    if not request.path == reverse('login'):
        if not request.path == reverse('register'):
            user = get_object_or_404(User, id = request.user.id)
            board_edit_perms = Board_Permission.objects.filter(Q(user=user) & (Q(permissions='owner') | Q(permissions='change_status')))
            organization_edit_perms = Organization_Permission.objects.filter(Q(user=user) & (Q(permissions='owner') | Q(permissions='boards_edit')))
            return {'board_edit_perms': board_edit_perms, 'organization_edit_perms': organization_edit_perms}
        else:
            return {}
    else:
        return {}

############
### Task ###
############

def check_task_edit(request) -> dict:
    """
    Function that adds 'task_edit_perms' to context
    Parameters
    ----------
        request: request
            session request
    """
    if not request.path == reverse('login'):
        if not request.path == reverse('register'):
            user = get_object_or_404(User, id = request.user.id)
            task_edit_perms = Board_Permission.objects.filter(Q(user=user) & (Q(permissions='owner') | Q(permissions='tasks_edit')))
            return {'task_edit_perms': task_edit_perms}
        else:
            return {}
    else:
        return {}