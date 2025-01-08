import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

CLIENT_ID = 'u-s4t2ud-c5829f79ff491d8cd54c3732c3414af2e0124487aefdafe69862641dbbdc6398'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:8000/oauth/oauth_callback'

def get_or_create_user(user_info):
    user, created = User.objects.get_or_create(
        username=user_info['login'],
        defaults={
            'email': user_info['email'],
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
        }
    )
    return user

def index(request):
    jwt_token = request.COOKIES.get('jwt')
    user_name = request.COOKIES.get('user_name')
    
    context = {
        'user_authenticated': jwt_token is not None,
        'user_name': user_name if user_name else '',
    }
    
    return render(request, 'oauth/index.html', context)

def login_view(request):
    authorize_url = f"https://api.intra.42.fr/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(authorize_url)

def logout_view(request):
    response = redirect('/oauth')
    response.delete_cookie('jwt')
    response.delete_cookie('user_name')
    return response

def oauth_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'No code returned'}, status=400)

    token_url = 'https://api.intra.42.fr/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        
        user_info_url = 'https://api.intra.42.fr/v2/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            
            user = get_or_create_user(user_info)
            print(user)

            refresh = RefreshToken.for_user(user)
            jwt_access_token = str(refresh.access_token)

            response = redirect('/oauth')
            response.set_cookie('jwt', jwt_access_token, httponly=True, secure=True)
            response.set_cookie('user_name', user_info['login'])
            
            return response
        else:
            return JsonResponse({'error': 'Failed to fetch user info'}, status=400)
    else:
        return JsonResponse({'error': 'Failed to obtain token'}, status=400)

def get_profile_picture(request):
    access_token = token_data['access_token']
    
    user_info_url = 'https://api.intra.42.fr/v2/me'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_info_response = requests.get(user_info_url, headers=headers)
    
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        return JsonResponse(user_info)
    else:
        return JsonResponse({'error': 'Failed to fetch user info'}, status=400)
