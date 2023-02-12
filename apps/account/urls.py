from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ChangePasswordView, 
    DeleteAccountView, 
    RegistrationView, 
    AccountActivationView, 
    RestorePasswordView, 
    SetRestoredPasswordView, 
    UserView, 
    UpdateUsernameImageAccountView,
    NewEmailView,
    SetNewEmailView,
    MentorActivationView,
    MentorRegistrationView
    )

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)   




urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('mentor-register/', MentorRegistrationView.as_view(), name='m-registration'),
    path('activate/<str:activation_code>/', AccountActivationView.as_view(), name='activation'),
    path('mentor-activate/<str:activation_code>/', MentorActivationView.as_view(), name='m-activation'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('restore-password/',  RestorePasswordView.as_view(), name='restored_password'),
    path('set-restored-password/', SetRestoredPasswordView.as_view(), name='set_restored_password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('user/', UserView.as_view()),
    path('update-first_last-name/<str:email>/', UpdateUsernameImageAccountView.as_view()),
    path('update-email/', NewEmailView.as_view()),
    path('set-new-email/', SetNewEmailView.as_view()),
]