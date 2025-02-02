from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from dashboard.models import Brigade, Equipment, Document, Category


class BrigadeForm(forms.ModelForm):
    class Meta:
        model = Brigade
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class EquipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['category','brigade', 'serial',
                  'name', 'manufacturer', 'documents',
                  'date_release', 'date_exploitation' ,'condition']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brigade': forms.Select(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'date_release': forms.DateTimeInput(format='%Y-%m-%d',
                                                attrs={'class': 'form-control text-info', 'type': 'date'}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d',
                                                     attrs={'class': 'form-control text-info', 'type': 'date',
                                                            'multiple': 'multiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['brigade'].queryset = Brigade.objects.order_by('name')

class EquipmentCreateByBrigadeForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['category', 'serial', 'name',
                  'condition', 'documents', 'date_release',
                  'date_exploitation', 'manufacturer']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'date_release': forms.DateTimeInput(format='%Y-%m-%d',
                                                attrs={'class': 'form-control text-info', 'type': 'date'}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d',
                                                     attrs={'class': 'form-control text-info', 'type': 'date',
                                                            'multiple': 'multiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EquipmentAddDocumentsForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['documents']


class UserCreateForm(forms.ModelForm):
    """Форма для создания пользователя с группами."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'groups', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'required checkbox', 'checked': 'checked', 'hidden': 'hidden'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'required checkbox', 'checked': 'checked', 'hidden': 'hidden'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'required checkbox'}),
            'groups': forms.CheckboxSelectMultiple(),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Поле пароль обязательно для заполнения")
        validate_password(password)
        return password

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        if groups and len(groups) > 1:
            raise forms.ValidationError("Можно выбрать только одну группу.")
        return groups

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CategoryCreateViewForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'parent', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.order_by('name')


from django.contrib.auth.models import Group, Permission


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']