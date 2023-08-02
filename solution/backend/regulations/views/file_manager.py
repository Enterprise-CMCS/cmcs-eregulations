from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.shortcuts import render
from ..integrations.box_integrations import get_authorization_url, get_oauth
from boxsdk import Client
from boxsdk.object.file import File
from boxsdk.exception import BoxOAuthException


class BoxCallbackView(View):
    def get(self, request, *args, **kwargs):

        # TBD - Implement the error handling will print the error for now.
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        error_description = request.GET.get('error_description')

        if not state:
            print("Invalid CSRF token. Authentication failed.")
        if error == 'access_denied':
            print("You denied access to this application.")

        if error_description:
            print(f"Error: {error_description}")

        # Create an instance of OAuth2
        oauth = get_oauth()

        # Authenticate the box_client
        oauth.authenticate(code)
        box_client = Client(oauth)

        # Render the file_manager.html template with the retrieved files
        context = self.get_context_data(box_client=box_client)
        return render(request, 'regulations/file_manager.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        box_client = kwargs.get('box_client')

        if box_client:
            root_folder = box_client.folder(folder_id='0')
            items = root_folder.get_items(limit=10, offset=0)

            files = []
            for item in items:
                if isinstance(item, File):
                    # Check if the file has a shared link and include it in the context
                    file_id = item.id
                    try:
                        shared_link = item.get().shared_link
                        shared_link_url = shared_link['url'] if shared_link else None
                    except BoxOAuthException as e:
                        if "Auth code doesn't exist or is invalid" in str(e):
                            try:
                                # Refresh the token using the refresh token
                                box_client.auth.refresh()
                                # box_client.auth.authenticate(refresh_token=box_client.auth.refresh_token)
                                # Retry getting the shared link after refreshing the token
                                shared_link = item.get().shared_link
                                shared_link_url = shared_link['url'] if shared_link else None
                            except BoxOAuthException as refresh_e:
                                print(f"Error refreshing token for file {file_id}: {refresh_e}")
                                shared_link_url = None
                        else:
                            print(f"Error retrieving shared link for file {file_id}: {e}")
                            shared_link_url = None

                    files.append((item, shared_link_url))
            context['files'] = files

        return context


class FileManagerView(TemplateView):
    template_name = 'regulations/file_manager.html'

    def get(self, request, *args, **kwargs):
        auth_url, csrf_token = get_authorization_url()
        request.session['box_csrf_token'] = csrf_token
        return redirect(auth_url)
