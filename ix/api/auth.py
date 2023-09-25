from django.contrib.auth import get_user_model


def get_request_user():
    """
    Get the current user from the request
    """
    # HAX: for now return the fake user
    user_model = get_user_model()
    return user_model.objects.earliest("id")
