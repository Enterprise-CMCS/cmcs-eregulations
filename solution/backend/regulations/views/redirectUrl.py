from django.shortcuts import redirect

def redirect_view(request):
    # Replace 'https://newdomain.com' with the actual URL where you want to redirect
    redirect_url = 'https://newdomain.com'
    return redirect(redirect_url)
