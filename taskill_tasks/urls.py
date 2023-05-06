from django.urls import path

from .views import (All_Organizations, board_edit_page, board_form,
                    change_task_status, delete_board, delete_organization,
                    delete_task, edit_assignees_to_task, give_board_permission,
                    give_organization_permission, homepage, leave_organization,
                    list_users_in_board, list_users_in_organization,
                    organization_detail, organization_edit_page,
                    organization_form, organization_search,
                    remove_board_permission, remove_organization_permission,
                    remove_user_from_organization, send_organization_request,
                    send_task_to_review, task_detail, task_edit_page,
                    task_form, task_make_progress, user_organization_list,
                    view_boards, view_user_board_permissions,
                    view_user_organization_permissions, view_user_tasks)

urlpatterns = [
    path('', homepage, name='homepage'),
    ### Organization urls ###
    # -- View -- #
    # -- Edit/Create -- #
    path('organization/create', organization_form, name='organization_creation'),
    path('organizations/', user_organization_list, name='organization_list'),
    path('organizations/all',All_Organizations.as_view(), name='all_organizations'),
    path('organization/<slug:slug>', organization_detail, name='organization_detail'),
    path('organization/<slug:slug>/edit', organization_edit_page, name='organization_edit_page'),
    path('organization/<slug:slug>/users', list_users_in_organization, name='list_users_in_organization'),
    # -- Requests -- #
    path('organization/search/', organization_search, name='organization_search'),
    path('organization/<slug:slug>/join', send_organization_request, name='send_organization_request'),
    path('organization/remove/<int:profile_id>', remove_user_from_organization, name='remove_user_from_organization'),
    path('organization/<slug:slug>/leave', leave_organization, name='leave_organization'),
    path('organization/<slug:slug>/delete', delete_organization, name='delete_organization'),
    # #- Permissions -# #
    path('organization/user-perms/<int:user_id>', view_user_organization_permissions, name='view_user_organization_permissions'),
    path('organization/<slug:slug>/give-permissions', give_organization_permission, name='give_organization_permission'),
    path('organization/<slug:slug>/remove-permission/<str:permission>', remove_organization_permission, name='remove_organization_permission'),
    ### End Organization urls ###
    ### Board urls ###
    # -- View -- #
    path('boards/', view_boards, name='view_boards'),
    path('board/<slug:slug>/users', list_users_in_board, name='list_users_in_board'),
    # -- Edit/Create -- #
    path('board/create', board_form, name='board_creation'),
    path('board/<slug:slug>/edit', board_edit_page, name='board_edit_page'),
    path('board/<slug:slug>/delete', delete_board, name='delete_board'),
    # #- Permissions -# #
    # -- View -- #
    path('board/user-perms/<int:user_id>', view_user_board_permissions, name='view_user_board_permissions'),
    # -- Add/Remove -- #
    path('board/<slug:slug>/give-permissions', give_board_permission, name='give_board_permission'),
    path('board/<slug:slug>/remove-permission/<str:permission>', remove_board_permission, name='remove_board_permission'),
    ### End Board urls ###
    ### Task urls ###
    # -- View -- #
    path('board/<slug:slug>/tasks', view_user_tasks, name='view_user_tasks'),
    path('board/<slug:board_slug>/task/<slug:task_slug>', task_detail, name='task_detail'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/edit', task_edit_page, name='task_edit_page'),
    # -- Edit/Create/Delete -- # 
    path('board/<slug:slug>/create-task', task_form, name='task_creation'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/add-user', edit_assignees_to_task, name='edit_assignees_to_task'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/make-progress', task_make_progress, name='task_make_progress'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/change-status', change_task_status, name='change_task_status'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/send-to-review', send_task_to_review, name='send_task_to_review'),
    path('board/<slug:board_slug>/task/<slug:task_slug>/delete', delete_task, name='delete_task'),
    ### End Task urls ###
]
