from boxsdk import OAuth2, Client
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .box_integration import get_box_client
from django.conf import settings
from django.http import HttpResponse




ACCESS_TOKEN = 'ymUw2NHOTkIqnTolQjO6fofOyO6G20xo',
REDIRECT_URL = 'http://localhost:8000/regulations/file_manager'

from django.shortcuts import render, redirect

class FileManagerView(TemplateView):
    template_name = 'regulations/file_manager.html'

    def get(self, request, *args, **kwargs):
        if request.path == '/authenticate/':
            return self.authenticate(request)
        elif request.path == '/callback/':
            return self.callback(request)
        return self.file_manager(request, *args, **kwargs)

    def authenticate(self, request):
        print("Inside authenticate method")
        auth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        auth_url, csrf_token = auth.get_authorization_url('http://localhost:8000/regulations/file_manager')
        request.session['csrf_token'] = csrf_token
        return redirect(auth_url[0])  # Extract the URL string from the tuple

    def callback(self, request):
        print("within callback")
        print(f"------the access token is: {ACCESS_TOKEN}")
        auth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        auth.authenticate(request.GET['code'])
        access_token, refresh_token = auth.get_tokens(request.GET['code'])
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        return redirect('file_manager')

    def file_manager(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("within get_context_data")
        print(f"------the access token is: {ACCESS_TOKEN}")
        access_token = self.request.session.get('access_token')
        refresh_token = self.request.session.get('refresh_token')

        if not access_token:
            raise PermissionDenied("Authentication required")  # Raise PermissionDenied exception

        auth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        if auth.access_token_expired():
            auth.refresh(ACCESS_TOKEN)  # Refresh the access token

            # Update the stored access token with the new value
            self.request.session['access_token'] = auth.access_token

        client = Client(auth)
        user = client.user().get()
        context['user_id'] = user.id

        # Retrieve the root folder ID
        root_folder = client.folder('0').get()
        root_folder_id = root_folder.id

        # Retrieve a list of files from the root folder
        root_folder_items = root_folder.get_items()

        file_list = []
        for item in root_folder_items:
            if isinstance(item, boxsdk.object.file.File):
                file_list.append(item)

        context['file_list'] = file_list

        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return redirect('authenticate')  # Redirect to the authentication view
