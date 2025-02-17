from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, Permission

from dashboard.models import Brigade, Equipment, Document, Category, UserProfile, Manufacturer


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
        fields = ['category', 'brigade', 'serial',
                  'name', 'manufacturer', 'documents',
                  'date_release', 'date_exploitation', 'condition', 'certificate_start', 'certificate_end']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brigade': forms.Select(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'documents': forms.SelectMultiple(attrs={'class': 'form-control', 'hidden': 'hidden'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'date_release': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'multiple': 'multiple'}),
            'certificate_start': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
            'certificate_end': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['brigade'].queryset = Brigade.objects.order_by('name')
        self.fields['documents'].queryset = Document.objects.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()  # Сохраняем ManyToMany поля
        return instance


class EquipmentCreateByBrigadeForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['category', 'serial', 'name',
                  'condition', 'documents', 'date_release',
                  'date_exploitation', 'manufacturer', 'certificate_start', 'certificate_end']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'documents': forms.SelectMultiple(attrs={'class': 'form-control', 'hidden': 'hidden'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'date_release': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'multiple': 'multiple'}),
            'certificate_start': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
            'certificate_end': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['documents'].queryset = Document.objects.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()  # Сохраняем ManyToMany поля
        return instance

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

    position = forms.CharField(
        max_length=100,
        required=False,  # Сделайте поле необязательным, если нужно
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,  # Сделайте поле необязательным, если нужно
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'groups', 'is_active', 'is_staff',
                  'is_superuser', 'position', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'position': forms.TextInput(attrs={'class': 'form-control'}),
            # 'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'required checkbox', 'checked': 'checked', 'hidden': 'hidden'}),
            'is_staff': forms.CheckboxInput(
                attrs={'class': 'required checkbox', 'checked': 'checked', 'hidden': 'hidden'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'required checkbox'}),
            'groups': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:  # Проверяем,
        # что это редактирование существующего объекта
        #     del self.fields['password']  # Удаляем поле 'password' из формы
        try:
            if self.instance:
                self.fields['position'].initial = getattr(self.instance, 'position', self.instance.profile.position)
                self.fields['phone_number'].initial = getattr(self.instance, 'phone_number', self.instance.profile.phone_number)
        except: pass

    def clean_password(self):
        password = self.cleaned_data['password']
        if not password:
            raise forms.ValidationError("Поле пароль обязательно для заполнения")
        validate_password(password)
        return password

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        if groups and len(groups) > 1:
            raise forms.ValidationError("Можно выбрать только одну группу.")
        elif len(groups) == 0:
            raise forms.ValidationError("Необходимо выбрать хотя бы одну группу.")
        return groups

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        position = self.cleaned_data['position']
        phone_number = self.cleaned_data['phone_number']
        password = self.cleaned_data.get('password')
        user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
            try:
                UserProfile.objects.create(user=user, position=str(position), phone_number=str(phone_number))
            except:
                profile = UserProfile.objects.get(user=user)
                profile.phone_number = phone_number
                profile.position = position
                profile.save()
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


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
