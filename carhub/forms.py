from django import forms
from django.forms import ModelForm, fields
from carhub.models import *

class RentCarForm(ModelForm):
    # city = forms.IntegerField()
    class Meta:
        model = Car
        exclude = ('user', 'created_at', 'updated_at', 'created_by', 'updated_by', 'details')
    
    # def __init__(self, *args, **kwargs):
    #     city = kwargs.pop('city', '')
    #     super(RentCarForm, self).__init__(*args, **kwargs)
    #     self.fie