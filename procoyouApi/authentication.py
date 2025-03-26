from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'  # Change from 'Token' to 'Bearer'
