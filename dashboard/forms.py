from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django_select2 import forms as s2forms

from dashboard.models import Brigade, Equipment, Document, Category, UserProfile, Manufacturer, WorkerActivity, \
    BrigadeActivity, WorkObject, Vehicle, VehicleMovement, OtherEquipment, OtherCategory, VehicleMovementEquipment

DATE_STYLE = {'style': 'width: 15rem;'}

class BrigadeForm(forms.ModelForm):
    class Meta:
        model = Brigade
        fields = ['name', 'description', 'customer', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
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
            'date_release': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date',
                                                            'multiple': 'multiple', 'style': DATE_STYLE['style']}),
            'certificate_start': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),
            'certificate_end': forms.DateTimeInput(format='%Y-%m-%d', attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),

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
            'date_release': forms.DateTimeInput(format='%Y-%m-%d',
                                                attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),
            'date_exploitation': forms.DateTimeInput(format='%Y-%m-%d',
                                                     attrs={'class': 'form-control text-info', 'type': 'date',
                                                            'multiple': 'multiple', 'style': DATE_STYLE['style']}),
            'certificate_start': forms.DateTimeInput(format='%Y-%m-%d',
                                                     attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),
            'certificate_end': forms.DateTimeInput(format='%Y-%m-%d',
                                                   attrs={'class': 'form-control text-info', 'type': 'date', 'style': DATE_STYLE['style']}),
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
        required=False,
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    brigade = forms.ModelChoiceField(
        queryset=Brigade.objects.all(),
        label="Бригада",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    brigade_start_date = forms.DateField(
        label="Дата начала работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )

    brigade_end_date = forms.DateField(
        label="Дата окончания работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )

    is_driver = forms.BooleanField(
        required=False,
        label="Водитель",
        widget=forms.CheckboxInput(attrs={'class': 'required checkbox'}))

    notes = forms.CharField(
        max_length=200,
        required=False,
        label="Примечания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'groups', 'is_active', 'is_staff',
                  'is_superuser', 'position', 'phone_number', 'brigade', 'brigade_start_date', 'brigade_end_date',
                  'is_driver', 'notes']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
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
        try:
            if self.instance:
                self.fields['position'].initial = getattr(self.instance, 'position', self.instance.profile.position)
                self.fields['phone_number'].initial = getattr(self.instance, 'phone_number',
                                                              self.instance.profile.phone_number)
                self.fields['brigade'].initial = getattr(self.instance, 'brigade', self.instance.profile.brigade)
                self.fields['brigade_start_date'].initial = getattr(self.instance, 'brigade_start_date',
                                                                    self.instance.profile.brigade_start_date)
                self.fields['brigade_end_date'].initial = getattr(self.instance, 'brigade_end_date',
                                                                  self.instance.profile.brigade_end_date)
                self.fields['is_driver'].initial = getattr(self.instance, 'is_driver', self.instance.profile.is_driver)
                self.fields['notes'].initial = getattr(self.instance, 'notes', self.instance.profile.notes)

            # if self.instance.pk:  # if the form is being used to update an existing user
            #     self.fields['password'].required = False
            #     self.fields['password'].widget.attrs['disabled'] = True
        except:
            pass

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
        brigade = self.cleaned_data.get('brigade')
        brigade_start_date = self.cleaned_data.get('brigade_start_date')
        brigade_end_date = self.cleaned_data.get('brigade_end_date')
        is_driver = self.cleaned_data.get('is_driver')
        notes = self.cleaned_data.get('notes')
        user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
            try:
                UserProfile.objects.create(user=user,
                                           position=str(position),
                                           phone_number=str(phone_number),
                                           brigade=brigade,
                                           brigade_start_date=brigade_start_date,
                                           brigade_end_date=brigade_end_date,
                                           is_driver=is_driver,
                                           notes=notes)
            except:
                profile = UserProfile.objects.get(user=user)
                profile.phone_number = phone_number
                profile.position = position
                profile.brigade = brigade
                profile.brigade_start_date = brigade_start_date
                profile.brigade_end_date = brigade_end_date
                profile.is_driver = is_driver
                profile.notes = notes
                profile.save()
        return user


class UserUpdateByBrigadeForm(forms.ModelForm):
    position = forms.CharField(
        max_length=100,
        required=False,
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    brigade_start_date = forms.DateField(
        label="Дата начала работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )
    brigade_end_date = forms.DateField(
        label="Дата окончания работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )
    is_driver = forms.BooleanField(
        required=False,
        label="Водитель",
        widget=forms.CheckboxInput(attrs={'class': 'required checkbox'}))

    notes = forms.CharField(
        max_length=200,
        required=False,
        label="Примечания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'position', 'phone_number',
                  'brigade_start_date', 'brigade_end_date', 'is_driver', 'notes']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if self.instance:
                self.fields['position'].initial = getattr(self.instance, 'position', self.instance.profile.position)
                self.fields['phone_number'].initial = getattr(self.instance, 'phone_number',
                                                              self.instance.profile.phone_number)
                self.fields['brigade_start_date'].initial = getattr(self.instance, 'brigade_start_date',
                                                                    self.instance.profile.brigade_start_date)
                self.fields['brigade_end_date'].initial = getattr(self.instance, 'brigade_end_date',
                                                                  self.instance.profile.brigade_end_date)
                self.fields['is_driver'].initial = getattr(self.instance, 'is_driver', self.instance.profile.is_driver)
                self.fields['notes'].initial = getattr(self.instance, 'notes', self.instance.profile.notes)
        except:
            pass

    def save(self, commit=True):
        user = super(UserUpdateByBrigadeForm, self).save(commit=False)
        position = self.cleaned_data['position']
        phone_number = self.cleaned_data['phone_number']
        brigade_start_date = self.cleaned_data.get('brigade_start_date')
        brigade_end_date = self.cleaned_data.get('brigade_end_date')
        is_driver = self.cleaned_data.get('is_driver')
        notes = self.cleaned_data.get('notes')
        if commit:
            user.save()
            self.save_m2m()
            profile = UserProfile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.position = position
            profile.brigade_start_date = brigade_start_date
            profile.brigade_end_date = brigade_end_date
            profile.is_driver = is_driver
            profile.notes = notes
            profile.save()
        return user


class UserUpdateStaffForm(forms.ModelForm):
    position = forms.CharField(
        max_length=100,
        required=False,
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    brigade = forms.ModelChoiceField(
        queryset=Brigade.objects.all(),
        label="Бригада",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    brigade_start_date = forms.DateField(
        label="Дата начала работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )
    brigade_end_date = forms.DateField(
        label="Дата окончания работы в бригаде",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control text-info'}),
        required=False
    )
    is_driver = forms.BooleanField(
        required=False,
        label="Водитель",
        widget=forms.CheckboxInput(attrs={'class': 'required checkbox'}))
    notes = forms.CharField(
        max_length=200,
        required=False,
        label="Примечания",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'brigade', 'position', 'phone_number',
                  'brigade_start_date', 'brigade_end_date', 'is_driver', 'notes']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if self.instance:
                self.fields['position'].initial = getattr(self.instance, 'position', self.instance.profile.position)
                self.fields['phone_number'].initial = getattr(self.instance, 'phone_number',
                                                              self.instance.profile.phone_number)
                self.fields['brigade'].initial = getattr(self.instance, 'brigade', self.instance.profile.brigade)
                self.fields['brigade_start_date'].initial = getattr(self.instance, 'brigade_start_date',
                                                                    self.instance.profile.brigade_start_date)
                self.fields['brigade_end_date'].initial = getattr(self.instance, 'brigade_end_date',
                                                                  self.instance.profile.brigade_end_date)
                self.fields['is_driver'].initial = getattr(self.instance, 'is_driver', self.instance.profile.is_driver)
                self.fields['notes'].initial = getattr(self.instance, 'notes', self.instance.profile.notes)
        except:
            pass

    def save(self, commit=True):
        user = super(UserUpdateStaffForm, self).save(commit=False)
        position = self.cleaned_data['position']
        phone_number = self.cleaned_data['phone_number']
        brigade_start_date = self.cleaned_data.get('brigade_start_date')
        brigade_end_date = self.cleaned_data.get('brigade_end_date')
        is_driver = self.cleaned_data.get('is_driver')
        notes = self.cleaned_data.get('notes')
        if commit:
            user.save()
            self.save_m2m()
            profile = UserProfile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.position = position
            profile.brigade_start_date = brigade_start_date
            profile.brigade_end_date = brigade_end_date
            profile.is_driver = is_driver
            profile.notes = notes
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


class WorkerActivityForm(forms.ModelForm):
    class Meta:
        model = WorkerActivity
        fields = ('date', 'work_type', 'brigade')
        widgets = {
            # 'user': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'brigade': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brigade'].queryset = Brigade.objects.order_by('name')


class BrigadeActivityForm(forms.ModelForm):
    class Meta:
        model = BrigadeActivity
        fields = ('date', 'work_type', 'work_object')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'work_object': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_object'].queryset = WorkObject.objects.order_by('short_name')

    def save(self, commit=True):
        brigade_activity = super(BrigadeActivityForm, self).save(commit=False)
        brigade_activity.save()
        return brigade_activity


class WorkObjectForm(forms.ModelForm):
    class Meta:
        model = WorkObject
        fields = ('hole', 'short_name', 'name',)
        widgets = {
            'hole': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     existing_locations = WorkObject.objects.values_list('name', 'name').distinct()  # Получаем кортежи (value, label)
    #     self.fields['name'].widget = forms.Select(choices=existing_locations)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['brand', 'model', 'number']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VehicleMovementForm(forms.ModelForm):
    class Meta:
        model = VehicleMovement
        fields = ['driver', 'vehicle', 'date', 'brigade_from', 'brigade_to']
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'brigade_from': forms.Select(attrs={'class': 'form-control'}),
            'brigade_to': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date', 'style': DATE_STYLE['style']}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = User.objects.order_by('last_name').filter(profile__is_driver=True)
        self.fields['driver'].label_from_instance = self.driver_label_from_instance

    def driver_label_from_instance(self, obj):
        return f"{obj.last_name} {obj.first_name}"


VehicleMovementEquipmentFormSet = inlineformset_factory(
    VehicleMovement,
    VehicleMovementEquipment,
    fields=('equipment', 'quantity', 'comment'),
    extra=10,
    can_delete=True,
    widgets = {
        'equipment': forms.Select(attrs={'class': 'form-control', 'autocomplete': 'on'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        'comment': forms.TextInput(attrs={'class': 'form-control'}),
    }
)

class OtherEquipmentForm(forms.ModelForm):
    class Meta:
        model = OtherEquipment
        fields = ['name', 'category', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class OtherCategoryForm(forms.ModelForm):
    class Meta:
        model = OtherCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VehicleMovementFilterForm(forms.Form):
    month = forms.IntegerField(required=False, label='Месяц', min_value=1, max_value=12, widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control'}))
    year = forms.IntegerField(required=False, label='Год', min_value=1900, max_value=2100, widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control'}))
    brigade_from = forms.ModelChoiceField(queryset=Brigade.objects.all(), required=False, label='Из бригады', widget=forms.Select(attrs={'class': 'form-control'}))
    brigade_to = forms.ModelChoiceField(queryset=Brigade.objects.all(), required=False, label='В бригаду', widget=forms.Select(attrs={'class': 'form-control'}))
    driver = forms.ModelChoiceField(queryset=User.objects.filter(profile__is_driver=True), required=False, label='Водитель', widget=forms.Select(attrs={'class': 'form-control'}))
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), required=False, label='Автомобиль', widget=forms.Select(attrs={'class': 'form-control'}))
    start_date = forms.DateField(required=False, label='Начальная дата', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, label='Конечная дата', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].queryset = User.objects.order_by('last_name').filter(profile__is_driver=True)
        self.fields['driver'].label_from_instance = self.driver_label_from_instance

    def driver_label_from_instance(self, obj):
        return f"{obj.last_name} {obj.first_name}"