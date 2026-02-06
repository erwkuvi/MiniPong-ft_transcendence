from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
#from .users import views
from friends.views import UserListView
from users.views import OTPLoginView, OAuth42LoginView, OAuth42CallbackView, OAuth42MatchView, OAuth42CallbackMatchView, OAuthGoogleUrlView, OAuthGoogleCallbackView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


admin.site.site_header = 'Ekuchel\'s Administration'
admin.site.index_title = 'Awesome Administration stuff'

urlpatterns = [
    path('friends/', include('friends.urls')),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/admin/', admin.site.urls),
    path('api/token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', lambda request: redirect('/api/admin/')),
    path('user_management/', include('users.urls')),
    path('auth/', include('djoser.urls')),
    path('42-login/', OAuth42LoginView.as_view(), name='42-login'),
    path('42-login-match/', OAuth42MatchView.as_view(), name='42-login-match'),
    path('42-callback/', OAuth42CallbackView.as_view(), name='42-callback'),
    path('42-callback-match/', OAuth42CallbackMatchView.as_view(), name='42-callback-match'),
    path('mfa/', OTPLoginView.as_view(), name='mfa'),
    #path('api/test/', include('notifications.urls')),
    path('google-login/', OAuthGoogleUrlView.as_view(), name='google-login'),
    path('google-callback/', OAuthGoogleCallbackView.as_view(), name='google-callback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# AVAILABLE ENDPOINTS FOR DJOSER(JWT)
# /auth/jwt/create/ (JWT getting a token and refresh)
# /auth/jwt/refresh/ (JWT )
# /auth/jwt/verify/ (JSON Web Token Authentication)
# /auth/users/
# /auth/users/me/
# /auth/users/confirm/
# /auth/users/resend_activation/
# /auth/users/set_password/
# /auth/users/reset_password/
# /auth/users/reset_password_confirm/
# /auth/users/set_username/
# /auth/users/reset_username/
# /auth/users/reset_username_confirm/

# /auth/42-login/
# /auth/42-callback/
# /auth/otp-login/

# user_management/players/
# user_management/players/{user_id} or me/
# user_management/matches/
