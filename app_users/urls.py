from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView

# from .views import home, new_invitation, accept_invitation

urlpatterns = [
    # re_path(r'home$', home, name="player_home"),
    re_path(r'login$',
            LoginView.as_view(template_name="users/login_form.html"),
            # LoginView.as_view(),
            name="user_login"),
    re_path(r'logout$',
            LogoutView.as_view(),
            name="user_logout"),
    # re_path(r'new_invitation$', new_invitation, name="player_new_invitation"),
    # re_path(r'accept_invitation/(?P<id>\d+)/$',
    #     accept_invitation,
    #     name="player_accept_invitation")
]
