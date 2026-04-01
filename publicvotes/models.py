import os
import six
import datetime
from pytils import translit

from django.utils import timezone
from datetime import datetime, date, time, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from django.contrib.auth.tokens import PasswordResetTokenGenerator


def make_upload_path(instance, filename):
    names = filename.split('.')
    new_filename = ''
    for name in names:
        if name != names[0]:
            new_filename += '.'
        new_filename += translit.slugify(name)

    path = 'vote_img/%s' % new_filename

    return path


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, theme, timestamp):
        return (
            six.text_type("Theme-")
            + six.text_type(theme.pk)
            + six.text_type(theme.title)
        )


theme_token_generator = TokenGenerator()


class Theme(models.Model):
	main_title = models.CharField(verbose_name="Текст главной страницы", max_length=250, blank=True)

	title = models.CharField(verbose_name="Блок голосования", max_length=250, blank=True)
	number = models.DecimalField(verbose_name="Номер", max_digits=2, decimal_places=0, default=1, blank=False)
	current = models.BooleanField("Текущее голосования", default=False)
	active = models.BooleanField("Активное голосования", default=False)

	zoom = models.BooleanField("Активное голосования", default=False)
	show_timer = models.BooleanField("Показывать таймер", default=False)
	count = models.DecimalField(verbose_name="Номер", max_digits=4, decimal_places=0, default=180, blank=False)

	theme_token = models.CharField(verbose_name="Токен", max_length=250, blank=True)

	registration_date = models.DateField(verbose_name="Дата создания", default=date.today)

	class Meta:
		ordering = ['title']
		verbose_name='Блок голосования'
		verbose_name_plural='Блоки голосований'

	def __str__(self):
		return self.title

	def get_status(self):
		STATUS = {
			False: '0',
			True: '1'
		}
		return STATUS[self.active]


class VotePart(models.Model):
	theme = models.ForeignKey(Theme, verbose_name="Голосование", on_delete=models.CASCADE, null=True, default=None, blank=True)
	name = models.CharField(verbose_name="Пункт голосования", max_length=250, blank=True)
	sub_name = models.CharField(verbose_name="Пункт голосования дополнительный", max_length=250, blank=True)
	number = models.DecimalField(verbose_name="Номер", max_digits=2, decimal_places=0, default=1, blank=False)

	photo = models.ImageField(verbose_name='Фото профиля', blank=True, null=True, upload_to = make_upload_path)

	class Meta:
		ordering = ['theme__title']
		verbose_name='Пункт голосования'
		verbose_name_plural='Пункты голосований'

	def __str__(self):
		return str(self.theme) + ' - ' + str(self.name)


class VoteCount(models.Model):
	vote_part = models.ForeignKey(VotePart, verbose_name="Голос", on_delete=models.CASCADE, null=True, default=None, blank=True)
	session_token = models.CharField(verbose_name="Токен сессии", max_length=250, blank=True, null=True, default="")

	class Meta:
		ordering = ['vote_part__theme__title']
		verbose_name='Голос'
		verbose_name_plural='Голоса'

	def __str__(self):
		return str(self.vote_part)


@receiver(post_save, sender=Theme)
def theme_post_save_handler(sender, **kwargs):
    theme = kwargs["instance"]
    if not theme.theme_token:
        theme.theme_token = theme_token_generator.make_token(theme)
        theme.save()


@receiver(post_delete, sender = VotePart)
def vote_part_post_delete_handler(sender, **kwargs):
	vote_part = kwargs['instance']

	if vote_part.photo:
		if os.path.isfile(vote_part.photo.path):
			os.remove(vote_part.photo.path)


@receiver(pre_save, sender = VotePart)
def vote_part_pre_save_handler(sender, **kwargs):
	vote_part = kwargs['instance']

	if not vote_part.pk:
		return False

	try:
		old_file = VotePart.objects.get(pk=vote_part.pk).photo
	except VotePart.DoesNotExist:
		return False

	if not old_file:
		return False

	new_file = vote_part.photo
	if not old_file==new_file:
		if os.path.isfile(old_file.path):
			os.remove(old_file.path)