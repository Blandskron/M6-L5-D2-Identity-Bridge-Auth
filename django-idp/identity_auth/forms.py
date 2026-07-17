from django import forms

from .models import EducationalResource


class EducationalResourceForm(forms.ModelForm):
    class Meta:
        model = EducationalResource
        fields = ("title", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
