from django.conf import settings
from django import forms
from datetime import date


from django.contrib.auth.models import User
from .models import Theme, VotePart


class ThemeForm(forms.ModelForm):
	class Meta:
		model = Theme
		fields = ('number', 'title', )

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control', 'autocomplete':'false'})
			self.fields[field].required=True


class VotePartForm(forms.ModelForm):
	class Meta:
		model = VotePart
		fields = ('number', 'theme', 'name', 'sub_name')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control', 'autocomplete':'false'})
			self.fields[field].required=True

