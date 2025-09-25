from .models import User
from .views import get_authenticated_user

def user_context(request):
    user = get_authenticated_user(request)
    return {
        'user': user
    }