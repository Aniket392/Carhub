from django.forms import ModelForm, fields
from carhub.models import *

class RentCarForm(ModelForm):
    class Meta:
        model = Car
        exclude = ('user', 'created_at', 'updated_at', 'created_by', 'updated_by')