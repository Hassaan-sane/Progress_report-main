from django import forms


class UsernameLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)

class UploadFileForm(forms.Form):
    file = forms.FileField()