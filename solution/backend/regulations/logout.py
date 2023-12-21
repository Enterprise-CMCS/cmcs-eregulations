from django.conf import settings


def eua_logout(request):
    id_token = request.session.get('oidc_id_token')

    if id_token is not None:
        # Use the id_token as needed in the logout request...
        logout_request = f'{settings.OIDC_END_EUA_SESSION}?' \
                         f'id_token_hint={id_token}&post_logout_redirect_uri=http://localhost:8000'
        return logout_request
    else:
        # Handle the case where id_token is not available
        return "id_token is not available in the user session."
