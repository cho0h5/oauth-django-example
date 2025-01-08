import requests
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import JsonResponse

CLIENT_ID = 'u-s4t2ud-c5829f79ff491d8cd54c3732c3414af2e0124487aefdafe69862641dbbdc6398'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:8000/oauth/oauth_callback'

def login_view(request):
    authorize_url = f"https://api.intra.42.fr/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(authorize_url)

def logout_view(request):
    return redirect('https://signin.intra.42.fr/users/sign_out')

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
        print(token_data)
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
    else:
        return JsonResponse({'error': 'Failed to obtain token'}, status=400)