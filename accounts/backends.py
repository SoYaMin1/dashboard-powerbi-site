from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Позволяет войти, указав имя пользователя или email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or password is None:
            return None

        login = username.strip()
        users = UserModel._default_manager.filter(
            Q(username=login) | Q(email__iexact=login)
        ).order_by("pk")

        for user in users:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        # Выравниваем время ответа, чтобы по нему нельзя было угадать, есть ли такой пользователь
        UserModel().set_password(password)
        return None