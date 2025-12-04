from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=[("client", "Client"), ("admin", "Admin")],
        label="Register as"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full p-3 rounded-xl border bg-gray-100"
            })
