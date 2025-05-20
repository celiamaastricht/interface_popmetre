from django import forms

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class AnalysisForm(forms.Form):
    files = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}), required=True)