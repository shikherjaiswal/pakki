
from django import forms
from dal import autocomplete
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Station, Train, Route
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.extras.widgets import SelectDateWidget


CLASS_CHOICE = [
    ('SL','Sleeper'),
    ('CC','Chair Car'),
    ('3A','Three-tier AC Sleeper'),
    ('2A','Second AC Sleeper'),
    ('1A','First AC Sleeper '),
    ('2S','Second Sitting'),
    ('3E','Second Sitting'),
    ('FC','Second Sitting'),
]
QUOTA_CHOICE = [
    ('GN','General Quota'),
    ('TQ', 'Tatkal Quota'),
    ('LD', 'Ladies Quota'),
    ('PT', 'Premium Tatkal Quota'),
]


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    email = forms.EmailField(max_length = 200, help_text = 'Required')
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class TrainsInfo(forms.Form):
    source = forms.ModelChoiceField(queryset=Station.objects.all(),
                                    widget=autocomplete.ModelSelect2(url='trains:station-autocomplete'))
    destination = forms.ModelChoiceField(queryset=Station.objects.all(),
                                         widget=autocomplete.ModelSelect2(url='trains:station-autocomplete'))
    # date = forms.DateField(input_formats=['%d-%m-%Y'])
    date = forms.DateField(widget = SelectDateWidget())
    #date = forms.DateField(widget=AdminDateWidget)
    cl = forms.CharField(label ='Class',widget = forms.Select(choices = CLASS_CHOICE))
    quota = forms.CharField(label = 'Quota' ,widget =forms.Select(choices = QUOTA_CHOICE) )
    class Meta:
        fields = ('source', 'destination', 'date', 'cl', 'quota')

class TrainRoute(forms.Form):
    train_number = forms.CharField(max_length=200)
    class Meta:
        fields = ('train_number')


class LiveTrain(forms.Form):
    train_number = forms.CharField(label ='TRAIN No.',max_length=200)
    date = forms.DateField(widget = SelectDateWidget())
    #date = forms.DateField(widget = AdminDateWidget)
    #date = forms.DateField(input_formats=['%d-%m-%Y'])
    class Meta:
        fields = ('train_number', 'date')


class PnrStatus(forms.Form):
    pnr_number = forms.CharField(label ='PNR No.',max_length=200)
    class Meta:
        fields = ('pnr_number')

class FareEnquiry(forms.Form):
    train_number = forms.CharField(label='TRAIN No.', max_length=200)
    #age = forms.CharField(label='AGE', max_length=50)
    source = forms.ModelChoiceField(queryset=Station.objects.all(),
                                    widget=autocomplete.ModelSelect2(url='trains:station-autocomplete'))
    destination = forms.ModelChoiceField(queryset=Station.objects.all(),
                                         widget=autocomplete.ModelSelect2(url='trains:station-autocomplete'))
    date = forms.DateField(widget=SelectDateWidget())
    #date = forms.DateField(input_formats=['%d-%m-%Y'])
    cl = forms.CharField(label ='Class',widget = forms.Select(choices = CLASS_CHOICE))
    quota = forms.CharField(label = 'Quota' ,widget =forms.Select(choices = QUOTA_CHOICE) )
    class Meta:
        #fields = ('train_number','age','source', 'destination', 'date', 'cl', 'quota')
        fields = ('train_number', 'source', 'destination', 'date', 'cl', 'quota')
