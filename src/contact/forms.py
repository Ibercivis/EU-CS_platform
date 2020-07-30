from django import forms
from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    name = forms.CharField(required=True)
    surname = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5,'cols': 40}), required=True)
    captcha = ReCaptchaField()



class SubmitterContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5,'cols': 40}), required=True)