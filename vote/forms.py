from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User as UserModel
from django.contrib.auth.models import User
	
from profileuser.models import Profile

User = get_user_model()


class UserLoginForm(forms.Form):
	username = forms.CharField(label = 'Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
	password = forms.CharField(label = 'Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


	def clean(self, *args, **kwargs):
		username = self.cleaned_data.get('username').lower()
		password = self.cleaned_data.get('password')
		
		if username and password:
			vaild_user = User.objects.filter(username=username)

			if not vaild_user:
				raise forms.ValidationError('Пользователь не существует!')

			if not vaild_user[0].is_active:
				raise forms.ValidationError('Адрес электронной почты не подтвержден!')

			user = authenticate(username = username, password = password)

			if not user:
				raise forms.ValidationError('Неверный пароль!')

		return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
	SPEAKER_TYPE = (
		('2', 'Участие без доклада'),
		('1', 'Выступление с докладом'),
	)

	SECTION_TYPE = (
		('', 'Выберите секцию'),
	)

	email = forms.EmailField(label = 'Ваш e-mail*', widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	surname = forms.CharField(label = 'Ваша фамилия*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	name  = forms.CharField(label = 'Ваше имя*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	name2  = forms.CharField(label = 'Ваше отчество', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	phone = forms.CharField(label = 'Телефон*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	work_place = forms.CharField(label = 'Название организации*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	work_part = forms.CharField(label = 'Название отдела (факультет, кафедра)', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	position = forms.CharField(label = 'Занимаемая должность', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	degree = forms.CharField(label = 'Ученая степень, ученое звание', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	speaker = forms.ChoiceField(label = 'Форма участия*', choices = SPEAKER_TYPE, widget=forms.Select(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	section = forms.ChoiceField(label = 'Секция*', choices = SECTION_TYPE, widget=forms.Select(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	
	agreement = forms.FileField(label = 'Скан-копия Согласия на обработку персональных данных*', required=True)

	password = forms.CharField(label = 'Задайте пароль*', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)

	def __init__(self, *args, **kwargs):
		super(UserRegistrationForm, self).__init__(*args, **kwargs)

		CHOICES = (
			('', 'Выберите секцию'),
		)
		sections = Section.objects.all().order_by('name')

		for section in sections:
			user_count = User.objects.filter(profile__section = section, is_active = True, profile__speaker = '2').count()
			if user_count < section.count:
				CHOICES = CHOICES + ((str(section.pk), section.name + ' - осталось мест: ' + str(section.count - user_count)),)

		self.fields['section'].choices=CHOICES


	class Meta:
		model = User
		fields = ('email',)


	def clean(self):
		data = self.cleaned_data
		email = data.get('email').lower()

		try:
			vaild_user = UserModel.objects.get(username=email)
		except UserModel.DoesNotExist:
			if email and UserModel.objects.filter(email=email).count()>0:
				raise forms.ValidationError('Используйте другой адрес электронной почты!')

			data['email'] = data['email'].lower()
			return data

		raise forms.ValidationError('Пользователь с таким email существует!')


class OrgRegistrationForm(forms.ModelForm):
	SPEAKER_TYPE = (
		('1', 'Выступление с докладом'),
		('2', 'Участие без доклада'),
	)

	email = forms.EmailField(label = 'Ваш e-mail*', widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	surname = forms.CharField(label = 'Ваша фамилия*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	name  = forms.CharField(label = 'Ваше имя*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	name2  = forms.CharField(label = 'Ваше отчество', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	phone = forms.CharField(label = 'Телефон*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	work_place = forms.CharField(label = 'Название организации*', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	work_part = forms.CharField(label = 'Название отдела (факультет, кафедра)', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	position = forms.CharField(label = 'Занимаемая должность', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	degree = forms.CharField(label = 'Ученая степень, ученое звание', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=False)
	speaker = forms.ChoiceField(label = 'Форма участия*', choices = SPEAKER_TYPE, widget=forms.Select(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)
	agreement = forms.FileField(label = 'Скан-копия Согласия на обработку персональных данных*', required=True)
	password = forms.CharField(label = 'Задайте пароль*', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete':'false'}), required=True)

	def __init__(self, *args, **kwargs):
		super(OrgRegistrationForm, self).__init__(*args, **kwargs)


	class Meta:
		model = User
		fields = ('email',)


	def clean(self):
		data = self.cleaned_data
		email = data.get('email').lower()

		try:
			vaild_user = UserModel.objects.get(username=email)
		except UserModel.DoesNotExist:
			if email and UserModel.objects.filter(email=email).count()>0:
				raise forms.ValidationError('Используйте другой адрес электронной почты!')

			data['email'] = data['email'].lower()
			return data

		raise forms.ValidationError('Пользователь с таким email существует!')


class ChangePasswordForm(forms.Form):
	oldpassword = forms.CharField(label = 'Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True)
	newpassword1 = forms.CharField(label = 'Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True)
	newpassword2 = forms.CharField(label = 'Новый пароль еще раз', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=True)

	def __init__(self, *args, **kwargs):
		self.username = kwargs.pop('username')
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		oldpass = self.cleaned_data['oldpassword']
		newpass1 = self.cleaned_data['newpassword1']
		newpass2 = self.cleaned_data['newpassword2']

		if oldpass and newpass1 and newpass2:
			user = authenticate(username = self.username, password = oldpass)
			if user is None:
				raise forms.ValidationError('Неверный пароль!')

			if newpass1 != newpass2:
				raise forms.ValidationError('Парли не совпали!')
		return self.cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
	class Meta:
		model = User
		fields = ['email']

	def __init__(self, *args, **kwargs):
		super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs.update({'class': 'form-control'})
		self.fields['email'].label = ''

	def clean(self):
		self.cleaned_data['email'] = self.cleaned_data['email'].lower()
		return self.cleaned_data


class CustomSetPasswordForm(SetPasswordForm):
	new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

	def __init__(self, *args, **kwargs):
		super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
		self.fields['new_password1'].label = 'Пароль'
		self.fields['new_password2'].label = 'Пароль еще раз'


	def clean_new_password2(self):
		password1 = self.cleaned_data.get('new_password1')
		password2 = self.cleaned_data.get('new_password1')
		return password2

