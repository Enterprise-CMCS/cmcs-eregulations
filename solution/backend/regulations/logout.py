from django.conf import settings


def eua_logout(request):
    id_token = request.session.get('oidc_id_token')
    # get the domain url from the request and add /login to the end
    logout_redirect_url = request.build_absolute_uri('/') + settings.STAGE_ENV + '/logout'

    # In the local environment where there is no STAGE_ENV, handle the possibility of //logout
    logout_redirect_url = logout_redirect_url.replace('//login', '/login').replace('/prod', '')

    if id_token is not None:
        # Use the id_token as needed in the logout request...
        logout_request = f'{settings.OIDC_END_EUA_SESSION}?' \
                         f'id_token_hint={id_token}&post_logout_redirect_uri={logout_redirect_url}'
        return logout_request
    else:
        # Handle the case where id_token is not available
        return "id_token is not available in the user session."
