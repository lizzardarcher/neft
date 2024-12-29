from django import forms

from dashboard.models import Brigade, Equipment


class BrigadeForm(forms.ModelForm):

    class Meta:
        model = Brigade
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class EquipmentCreateByBrigadeForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['category', 'serial', 'name', 'condition', 'documents', 'date_release', 'date_exploitation' ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'documents': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'date_release': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'multiple': 'multiple'}),
        }