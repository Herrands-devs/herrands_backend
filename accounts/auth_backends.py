from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:
            email = kwargs.get('contact', None)
            if email is None:
                email = kwargs.get('username', None)
            user = UserModel.objects.get(email=email)
            print(user)
            print(user.otp)
            if user.otp ==(kwargs.get('password', None)):
                print('yes')
                return user
        except UserModel.DoesNotExist:
            return None
        return None