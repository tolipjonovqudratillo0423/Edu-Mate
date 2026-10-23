from rest_framework_simplejwt.tokens import RefreshToken

def for_user(user):
    token = RefreshToken.for_user(user)
    
    return {
        "access": str(token.access_token),
        "refresh": str(token),
    }