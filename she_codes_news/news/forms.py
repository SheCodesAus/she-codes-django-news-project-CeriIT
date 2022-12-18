from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import NewsStory


User = get_user_model()
class StoryForm(ModelForm):
    class Meta:
        model = NewsStory
        fields = ['title', 'pub_date', 'content','img_url']
        widgets = {
            'pub_date': forms.DateInput(format=('%m/%d/%Y'),
            attrs={'class':'form-control',
            'placeholder':'Select a date',
            'type':'date'}),
            }

ORDER_CHOICE = (
    ('', "newest first"),
    ('oldfirst', "oldest first")
)
class FilterForm(forms.Form):
    order = forms.ChoiceField(label="order", choices=ORDER_CHOICE, required=False)
    author = forms.ModelChoiceField(label="author", queryset=User.objects.all(), required=False)
    search = forms.CharField(label="search", required=False)
