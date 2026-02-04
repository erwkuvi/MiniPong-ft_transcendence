import requests
import pyotp
import secrets
import string
from urllib.parse import urlencode 
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, action
from rest_framework import generics, viewsets, status, views, exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny#, IsAdminUser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin#CreateModelMixin
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import User, PlayerProfile, Match, Tournament
from django.http import HttpResponseRedirect
from django.conf import settings  # Ensure this import is correct
from .serializers import UserSerializer, PlayerProfileSerializer, MatchSerializer, UserCreateSerializer, OTPLoginSerializer, OTPActivateSerializer, OTPActiveToTrueSerializer, OTPDeactivateSerializer, SimpleLoginSerializer, TournamentSerializer, ExitTournamentSerializer, MatchTournamentSerializer, ScoreRetrieveSerializer, ExitMultiplayerSerializer, TournamentIdSerializer
import os

#from .permissions import IsAdminOrReadOnly
#from django.http import JsonResponse


class ExitMultiplayerViewSet(viewsets.ViewSet):
    serializer_class = ExitMultiplayerSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = ExitMultiplayerSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SimpleLoginViewSet(viewsets.GenericViewSet):
    serializer_class = SimpleLoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.save()  
        return Response({
            "message": "Authentication successful",
            "user_id": user_data.get('user_id'),
            "display_name": user_data.get('display_name')
        }, status=status.HTTP_200_OK)


class CreateUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
                {"success": True, "message": "Registration Successful!"}, 
                status=status.HTTP_200_OK
                )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PlayerProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] # for development
    parser_classes = [MultiPartParser, FormParser]  # Add parsers for file uploads

    def list(self, request, *args, **kwargs):
        queryset = PlayerProfile.objects.all()
        serializer = PlayerProfileSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):  # This method is called a custom action
        player_profile = PlayerProfile.objects.get(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = PlayerProfileSerializer(player_profile, context=self.get_serializer_context())
            data = serializer.data
            data['username'] = request.user.username
            return Response(data)
        elif request.method == 'PATCH':
            serializer = PlayerProfileSerializer(
                player_profile, data=request.data, context=self.get_serializer_context(), partial=True)  # Ensure partial updates
            if not serializer.is_valid():
                print(serializer.errors)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [AllowAny] # for development
    #permission_classes = [IsAuthenticated]

#    def get_queryset(self):
#        if self.request.user.is_staff:
#            return Match.objects.all()
#
#        (id, created) = Match.objects.only('id').get_or_create(id=self.request.user.id)
#        return Match.objects.filter(id=id)
#return Match.objects.filter(id=self.request.user.id)



# ---------------OAuth 42 API------------------------------------------------------------------------------------
# class GoogleLoginView(views.APIView):
    # permission_classes = [AllowAny]
class OAuth42LoginView(views.APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get(self, request):
        # Generate a secure random string for the state parameter to prevent CSRF attacks
        characters = string.ascii_letters + string.digits
        state = ''.join(secrets.choice(characters) for _ in range(30))  # Adjust length as needed
        request.session['oauth_state'] = state
        # Construct the URL with query parameters

        auth_url = (
                f"{settings.API_42_AUTH_URL}"
                f"?client_id={settings.INTRA_UID_42}"
                f"&redirect_uri={settings.API_42_REDIRECT_URI}"
                f"&response_type=code"
                f"&scope=public"
                f"&state={state}"
                )
        # Redirect the user to the 42 authorization URL
        return redirect(auth_url)

class OAuth42MatchView(views.APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get(self, request):
        # Generate a secure random string for the state parameter to prevent CSRF attacks
        characters = string.ascii_letters + string.digits
        state = ''.join(secrets.choice(characters) for _ in range(30))  # Adjust length as needed
        request.session['oauth_state'] = state
        # Construct the URL with query parameters

        auth_url = (
                f"{settings.API_42_AUTH_URL}"
                f"?client_id={settings.INTRA_UID_42}"
                f"&redirect_uri={settings.API_42_REDIRECT_URI_MATCH}"
                f"&response_type=code"
                f"&scope=public"
                f"&state={state}"
                )
        # Redirect the user to the 42 authorization URL
        return redirect(auth_url)
    


def save_avatar_locally(avatar_url, player_profile, user):
    response = requests.get(avatar_url)
    if response.status_code == 200:
        # Check if there is an existing avatar and delete it
        if player_profile.avatar and player_profile.avatar.name != 'avatar.png':
            player_profile.avatar.delete(save=False)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        player_profile.avatar.save(f"{user.username}_avatar.jpg", File(img_temp), save=True)



class OAuth42CallbackMatchView(views.APIView):

    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        try:
            # 1. Get authorization code from request
            code = request.data.get('code')
            if not code:
                raise ValueError("No authorization code provided")

            # 2. Exchange code for access token
            token_response = requests.post(
                'https://api.intra.42.fr/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': settings.INTRA_UID_42,
                    'client_secret': settings.INTRA_SECRET_42,
                    'code': code,
                    'redirect_uri': settings.API_42_REDIRECT_URI
                }
            )
            
            if token_response.status_code != 200:
                raise ValueError("Failed to exchange code for token")
            
            token_data = token_response.json()
            access_token = token_data['access_token']

            # 3. Fetch user information
            user_info_response = requests.get(
                'https://api.intra.42.fr/v2/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if user_info_response.status_code != 200:
                raise ValueError("Failed to retrieve user information")
            
            user_info = user_info_response.json()

            # 4. Create or get user
            try:
                user = User.objects.get(email=user_info.get('email'))
            except User.DoesNotExist:
                raise ValueError("User not found")

            try:
                player_profile = PlayerProfile.objects.get(
                    user=user,
                    display_name=user_info.get("displayname"),
                )
            except PlayerProfile.DoesNotExist:
                raise ValueError("Player profile does not exist")

            # Return only user_id and display_name
            return Response({
                "user_id": user.id,
                "display_name": player_profile.display_name
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        try:
            code = request.query_params.get('code')
            state = request.query_params.get('state')
            session_state = request.session.get('oauth_state')
            redirect_uri = request.query_params.get('redirect_uri', settings.FRONTEND_URL)
            
            if not code or not state:
                raise AuthenticationFailed("Missing code or state in the callback response.")
            
            # Validate state parameter
            if state != session_state:
                raise AuthenticationFailed("Invalid state parameter.")
            
            # Exchange code for access token
            token_response = requests.post(
                'https://api.intra.42.fr/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': settings.INTRA_UID_42,
                    'client_secret': settings.INTRA_SECRET_42,
                    'code': code,
                    'redirect_uri': settings.API_42_REDIRECT_URI_MATCH,
                }
            )

            if token_response.status_code != 200:
                raise AuthenticationFailed("Failed to obtain access token.")

            token_data = token_response.json()
            access_token = token_data.get('access_token')

            # Fetch user info from 42 API
            user_info_response = requests.get(
                'https://api.intra.42.fr/v2/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            if user_info_response.status_code != 200:
                raise AuthenticationFailed("Failed to obtain user information.")
            
            user_info = user_info_response.json()

            # Get user's data
            try:
                user = User.objects.get(email=user_info.get('email'))
            except User.DoesNotExist:
                raise ValueError("User not found")

            try:
                player_profile = PlayerProfile.objects.get(
                    user=user,
                    display_name=user_info.get("displayname"),
                )
            except PlayerProfile.DoesNotExist:
                raise ValueError("Player profile does not exist")

            redirect_url = f"{redirect_uri}/play/?user_id={user.id}&display_name={player_profile.display_name}"

            # Return a redirect to the frontend URL
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            error_message = str(e)
            frontend_url = settings.FRONTEND_URL + "/play"
    
            return HttpResponseRedirect(f"{frontend_url}?error={error_message}")



class OAuth42CallbackView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # 1. Get authorization code from request
            code = request.data.get('code')
            if not code:
                raise ValueError("No authorization code provided")

            # 2. Exchange code for access token
            token_data = self.get_access_token(code)
            access_token = token_data['access_token']

            # 3. Fetch user information
            user_info = self.get_user_info(access_token)

            # 4. Create or get user
            user, created = User.objects.get_or_create(
                email=user_info.get('email'),
                defaults={
                    'username': user_info.get('login'),
                    'auth_provider': "42api"
                },
            )

            # Only set displayname & avatar if the user is new
            if created:
                user.displayname = user_info.get("displayname")
                user.save()

            player_profile, profile_created = PlayerProfile.objects.get_or_create(
                user=user,
                defaults={'display_name': user_info.get("displayname")}
            )

            # Save avatar only if the user is new or the profile is new
            avatar_url = user_info.get("image", {}).get("versions", {}).get("medium")
            if avatar_url and (created or profile_created):
                save_avatar_locally(avatar_url, player_profile, user)

            # 5. Generate JWT tokens
            return Response(self.generate_tokens(user, player_profile), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            code = request.query_params.get('code')
            state = request.query_params.get('state')
            session_state = request.session.get('oauth_state')

            if not code or not state:
                raise AuthenticationFailed("Missing code or state in the callback response.")

            # Validate state parameter
            if state != session_state:
                raise AuthenticationFailed("Invalid state parameter.")

            # Exchange code for access token
            token_data = self.get_access_token(code)
            access_token = token_data.get('access_token')

            # Fetch user info
            user_info = self.get_user_info(access_token)

            # Get user data
            email = user_info.get("email")
            username = user_info.get("login")
            displayname = user_info.get("displayname")
            avatar_url = user_info.get("image", {}).get("versions", {}).get("medium")

            # Check if user exists, if not, create them
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': username, 'auth_provider': "42api"}
            )

            # Only update displayname if the user is newly created
            if created:
                user.displayname = displayname
                user.save()

            player_profile, profile_created = PlayerProfile.objects.get_or_create(
                user=user,
                defaults={'display_name': displayname}
            )

            # Save avatar only if the user is new or profile is new
            if avatar_url and (created or profile_created):
                save_avatar_locally(avatar_url, player_profile, user)

            # Generate JWT token
            tokens = self.generate_tokens(user, player_profile)
            frontend_url = f"{settings.FRONTEND_URL}/login/callback?access={tokens['access']}&refresh={tokens['refresh']}"

            return redirect(frontend_url)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_access_token(self, code):
        """Exchange authorization code for an access token."""
        response = requests.post(
            'https://api.intra.42.fr/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': settings.INTRA_UID_42,
                'client_secret': settings.INTRA_SECRET_42,
                'code': code,
                'redirect_uri': settings.API_42_REDIRECT_URI
            }
        )
        if response.status_code != 200:
            raise AuthenticationFailed("Failed to obtain access token.")
        return response.json()

    def get_user_info(self, access_token):
        """Fetch user info from 42 API."""
        response = requests.get(
            'https://api.intra.42.fr/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if response.status_code != 200:
            raise AuthenticationFailed("Failed to obtain user information.")
        return response.json()

    def generate_tokens(self, user, player_profile):
        """Generate JWT access and refresh tokens."""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'auth_provider': user.auth_provider,
                'displayname': player_profile.display_name,
            }
        }



# ---------------End of OAuth 42 API------------------------------------------------------------------------------------

# ---------------OTPLOGIN ---------------------------------------------------------------------------------------------

class OTPActivateViewSet(viewsets.GenericViewSet):
    serializer_class = OTPActivateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_data = serializer.save()
        return Response(otp_data, status=status.HTTP_200_OK)

class OTPActiveToTrueViewSet(viewsets.GenericViewSet):
    serializer_class = OTPActiveToTrueSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_data = serializer.save()
        return Response(otp_data, status=status.HTTP_200_OK)

class OTPDeactivateViewSet(viewsets.GenericViewSet):
    serializer_class = OTPDeactivateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_data = serializer.save()
        return Response(otp_data, status=status.HTTP_200_OK)

class OTPLoginView(generics.GenericAPIView):
    serializer_class = OTPLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If validation passes, JWT tokens are returned from serializer's `validate` method
        tokens = serializer.validated_data
        return Response(tokens, status=status.HTTP_200_OK)




# logout view
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("Logout error:", str(e))
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------------- Tournament Endpoints ----------------
class TournamentCreateViewSet(viewsets.GenericViewSet):
    serializer_class = TournamentSerializer
    #permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tournament.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matches = serializer.save()

        response_data = []
        
        for match in matches:
            match_data = {
                'id': match.id,
                'player1': match.player1_id,
                'player2': match.player2_id,
                'idx': match.idx,
                'level': match.level,
                'tournament': match.tournament_id,
                'mode': match.mode
            }
            response_data.append(match_data)
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class ExitTournamentViewSet(viewsets.GenericViewSet):
    serializer_class = ExitTournamentSerializer
    #permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)


class MatchTournamentViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.filter(mode='tournament')
    serializer_class = MatchTournamentSerializer
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ScoreRetrieveViewSet(viewsets.GenericViewSet):
    serializer_class = ScoreRetrieveSerializer
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        if isinstance(result, dict) and "message" in result:
            return Response(result, status=status.HTTP_200_OK)
        
        return Response(self.get_serializer(result).data, status=status.HTTP_201_CREATED)


class TournamentViewSet(viewsets.ViewSet):
    #permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, pk=None):
        serializer = TournamentIdSerializer(data={'tournament_id': pk})
        if serializer.is_valid():
            matches_data = serializer.create(serializer.validated_data)
            return Response(matches_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
