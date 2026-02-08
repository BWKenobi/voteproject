import os
import datetime

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None, blank=True)

	first_name = models.CharField(verbose_name="Имя", max_length=30, blank=True)
	middle_name = models.CharField(verbose_name="Отчество", max_length=30, blank=True)
	last_name = models.CharField(verbose_name="Фамилия", max_length=50, blank=True)

	policy_success= models.BooleanField("Согласие на обработку персональных данных", default=False)
	cookies_agree = models.BooleanField("Согласие с куки", default=False)

	admin_access = models.BooleanField("Права Администратора", default=False)

	registration_date = models.DateField(verbose_name="Дата регистрации", default=datetime.date.today)


	def __str__(self):
		if self.pk == 1:
			return 'admin'
		if self.user.is_active:
			return self.get_name()
		return self.user.username + ' (not active)'


	def get_full_name(self):
		if self.last_name:
			if self.middle_name:
				return self.last_name + ' ' + self.first_name + ' ' + self.middle_name
			return self.last_name + ' ' + self.first_name 
		return self.first_name


	def get_name(self):
		if self.last_name:
			return self.first_name + ' ' + self.last_name
		if self.first_name:
			return self.first_name
		return self.user.username


	def get_short_name(self):
		if self.last_name:
			return self.last_name + ' ' + self.first_name[0] + '.'
		return self.first_name


	def get_io_name(self):
		if self.middle_name:
			return self.first_name + ' ' + self.middle_name 
		return self.first_name 


######################################################################
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

