from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User  # this model is provided by django


class RegisterationFrom(UserCreationForm):
    #  here I'm just adding my front-end customizations for better layout
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # apply those args on the input with the (id or name - ngl I don't know for sure (⌬̀⌄⌬́)(⌬̀⌄⌬́)_へ__(‾◡◝ )> -) = 'first_name'
        # equivalent in html to --> <input type="text" class="form-control" name="first_name" id="first_name" placeholder="Your First Name" required>
        self.fields["first_name"].widget.attrs.update({
            'required': '',
            'name': 'first_name',
            'id': 'first_name',
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Your First Name'
        })
        self.fields["last_name"].widget.attrs.update({
            'required': '',
            'name': 'last_name',
            'id': 'last_name',
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Your Last Name'
        })
        self.fields["username"].widget.attrs.update({
            'required': '',
            'name': 'username',
            'id': 'username',
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Your Username'
        })
        self.fields["email"].widget.attrs.update({
            'required': '',
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
        self.fields["password1"].widget.attrs.update({
            'required': '',
            'name': 'password1',
            'id': 'password1',
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Choose a powerfull password'
        })
        self.fields["password2"].widget.attrs.update({
            'required': '',
            'name': 'password2',
            'id': 'password2',
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Retype your password'
        })

    class Meta:  # here I'm overriding the simple default django registeration form (it gives just username and password, but I added other fields)
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]


class SignInForm(AuthenticationForm):  # the same as above
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            'required': '',
            'name': 'username',
            'id': 'username',
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Your Username'
        })
        self.fields["password"].widget.attrs.update({
            'required': '',
            'name': 'password',
            'id': 'password',
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Your password'
        })

    class Meta:
        model = User
        fields = ["username", "password"]
