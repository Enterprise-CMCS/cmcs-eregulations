from rest_framework_simplejwt.tokens import RefreshToken


# Returns an empty string if none instead of "None"
def check_string_value(check_string):
    return check_string if check_string else ''


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
