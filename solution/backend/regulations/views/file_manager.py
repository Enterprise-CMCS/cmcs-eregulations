from django.shortcuts import redirect
from django.views.generic import TemplateView
from ..integrations.box_integrations import get_box_client, get_authorization_url


class FileManagerView(TemplateView):
    template_name = 'regulations/file_manager.html'

    def get(self, request, *args, **kwargs):
        # Check if the request contains the authorization code
        auth_url, csrf_token = get_authorization_url()
        print(f"------ the auth url is {auth_url}")
        print(f"------ the csrf token is {csrf_token}")
        print(f"------ the code is {request.GET}")
        if 'code' in request.GET:
            # Retrieve the authorization code from the request
            auth_code = request.GET['code']
            # Call the authenticate method to exchange the auth code for access and refresh tokens
            access_token, refresh_token = get_box_client().authenticate(auth_code)
            # Store the tokens in the session
            request.session['box_access_token'] = access_token
            # Redirect to the FileManagerView to display the files
            return redirect('file_manager')
        auth_url, csrf_token = get_authorization_url()
        request.session['box_csrf_token'] = csrf_token
        return redirect(auth_url)

    def box_callback(self, auth_code):
        print(f"current_user: {current_user}")
        print(request.args)
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        error_description = request.args.get('error_description')

        user = Users.query.filter_by(csrf_token=state).first()
        if user == None:
            msg = 'User not found'
        elif state != user.csrf_token:
            msg = 'CSRF token is invalid'
        elif error == 'access_denied':
            msg = 'You denied access to this application'
        else:
            msg = error_description

        if msg != None:
            return render_template('accounts/login-box.html', msg=msg)

        # Redirect to the FileManagerView to display the files
        return redirect('file_manager')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        access_token = self.request.GET.get('access_token')
        print(f"------ the access token is {access_token}")
        if access_token:
            box_client = get_box_client(access_token)
            root_folder = box_client.folder(folder_id='0')
            items = root_folder.get_items(limit=10, offset=0)

            files = []
            for item in items:
                if isinstance(item, boxsdk.object.file.File):
                    files.append(item)

            context['files'] = files

        return context
