from django.urls import path

from .views import (accept_request, find_profile, friend_list, profile,
                    profile_edit, profile_edit_email, profile_search, register,
                    remove_manager, remove_request, send_friend_request,
                    send_manager_request, unfriend, update_profile_image,
                    user_login, user_logout, user_requests)

urlpatterns = [
    # Login/Logout/Register #
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    # End Login/Logout/Register #
    # Profile #
    path('profile/', profile, name='profile'),
    path('profile/<slug:slug>', find_profile, name='find_profile'),
    path('profile/search/', profile_search, name='profile_search'),
    path('profile-edit/', profile_edit, name='profile_edit'),
    path('profile/edit/email', profile_edit_email, name='profile_edit_email'),
    path('profile/edit/image', update_profile_image, name='update-image'),
    # End Profile #
    # Requests #
    path('request/send/friend/<int:user_id>', send_friend_request, name='send_friend_request'),
    path('request/send/manager/<int:user_id>', send_manager_request, name='send_manager_request'),
    path('request/<int:request_id>/accept', accept_request, name='accept_request'),
    path('request/<int:request_id>/remove', remove_request, name='remove_request'),
    path('unfriend/<int:user_id>', unfriend, name='unfriend'),
    path('remove-manager/<int:user_id>', remove_manager, name='remove_manager'),
    # End Requests #
    path('friend-list/', friend_list, name='friend_list'),
    path('requests/', user_requests, name='user_requests'),
    
]

