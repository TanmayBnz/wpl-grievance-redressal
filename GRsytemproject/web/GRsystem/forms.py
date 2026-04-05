from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Complaint

REGISTRATION_USER_TYPES = (
    ('student', 'Student'),
    ('teaching_staff', 'Teaching Staff'),
    ('non_teaching_staff', 'Non-Teaching Staff'),
)


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email


class UserProfileform(forms.ModelForm):
    type_user = forms.ChoiceField(
        choices=REGISTRATION_USER_TYPES,
        label='I am registering as',
        initial='student',
    )

    class Meta:
        model = Profile
        fields = ('collegename', 'type_user', 'Branch', 'contactnumber')


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email


class UserProfileUpdateform(forms.ModelForm):
    collegename = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    Branch = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    type_user = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Role')

    class Meta:
        model = Profile
        fields = ('collegename', 'type_user', 'Branch', 'contactnumber')


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('Subject', 'Type_of_complaint', 'department', 'Description')
        labels = {
            'Type_of_complaint': 'Category',
            'department': 'Department (optional)',
        }


class StatusUpdateForm(forms.ModelForm):
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a remark (optional)'}),
        required=False,
        label='Remarks',
    )

    class Meta:
        model = Complaint
        fields = ('status', 'remarks')
        help_texts = {'status': None}


# Legacy alias kept for any references
statusupdate = StatusUpdateForm
