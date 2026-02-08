import datetime
import json

from django.db.models import Q
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site

from django.conf import settings

import base64

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from .tokens import accaunt_activation_token

#from profileuser.views import delete_unconfirmed_users

from profileuser.models import Profile
from publicvotes.models import Theme, VotePart, VoteCount

from .forms import UserLoginForm


def home_view(request, token = ''):
	if not request.session.session_key:
		request.session.create()

	session_token = request.session.session_key

	if not token:
		return render(request, 'blank.html')

	theme = Theme.objects.filter(theme_token = token, active = True).first()

	if not theme:
		return render(request, 'blank.html')

	vote_parts = None
	vote_count = VoteCount.objects.filter(session_token = session_token, vote_part__theme = theme).first()
	if not vote_count:
		vote_parts = VotePart.objects.filter(theme = theme).order_by('number')

	print(theme)
	args = {
		'theme': theme,
		'vote_parts': vote_parts,
		'vote_count': vote_count
	}

	return render(request, 'my_vote.html', args)


@login_required(login_url='/login')
def control_view(request):
	if not request.user.profile.admin_access:
		return redirect ('home')

	themes = Theme.objects.all().order_by('number')
	sorted_counts = {}
	zoom = False
	for theme in themes:
		if theme.zoom:
			zoom = True

		votepart_counts = {}
		voteparts= VotePart.objects.filter(theme = theme).order_by('number')
		for votepart in voteparts:
			votepart_counts[votepart] = VoteCount.objects.filter(vote_part = votepart).count()

		sorted_counts[theme.pk] =  dict(sorted(votepart_counts.items(), key=lambda x: x[1], reverse=True))


	args = {
		'themes': themes,
		'votepart_counts': votepart_counts,
		'sorted_counts': sorted_counts,
		'zoom': zoom
	}

	return render(request, 'control_view.html', args)


@login_required(login_url='/login')
def concerted_view(request):
	if not request.user.profile.admin_access:
		return redirect ('home')

	theme_token = ''
	active = False
	seconds = 0

	theme = Theme.objects.filter(current = True).first()
	if theme:
		current_site = get_current_site(request)
		protocol = 'http'
		if request.is_secure():
			protocol = 'https'

		url = protocol + '://' + current_site.domain + '/vote/' + theme.theme_token

		theme_token = theme.theme_token
		active= theme.active
		seconds = int(theme.count)

		vote_counts = {}
		vote_parts = VotePart.objects.filter(theme = theme).order_by('number')
		for vote_part in vote_parts:
			vote_counts[vote_part.pk] = VoteCount.objects.filter(vote_part = vote_part).count()

	args = {
		'theme': 'theme',
		'url': url,
		'theme_token': theme_token,
		'active': active,
		'seconds': seconds,
		'vote_parts': vote_parts,
		'vote_counts': vote_counts
	}
	return render(request, 'main_vote.html', args)


def policy_view(request):
	args = {
		'menu': 'policy',
	}

	return render(request, 'policy.html', args)


def login_view(request):
	form = UserLoginForm(request.POST or None)
	next_ = request.GET.get('next')
	modal = False

	if form.is_valid():
		username = request.POST.get('username').lower()
		password = request.POST.get('password')
		user = authenticate(username = username.strip(), password = password.strip())
		
		login(request, user)
		next_post = request.POST.get('next')
		redirect_path = next_ or next_post or '/'


		return redirect(redirect_path)

	args = {
		'form': form
	}
	return render(request, 'login.html', args)


def logout_view(request):
	logout(request)
	return redirect('home')

	
####################################################################
def allow_cookies(request):
	request.session['coockes'] = '1'

	if request.user.is_authenticated:
		request.user.profile.cookies_agree = True
		request.user.profile.save()

	return HttpResponse('1')


def zoom(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	themes = Theme.objects.all().order_by('number')
	for theme in themes:
		theme.zoom = True
		theme.save()
	return HttpResponse('1')


def unzoom(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	themes = Theme.objects.all().order_by('number')
	for theme in themes:
		theme.zoom = False
		theme.save()
	return HttpResponse('1')


@csrf_exempt
def current(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	if request.method=='POST':
		pk = request.POST['pk']
		theme = Theme.objects.filter(pk = pk).first()
		all_themes = Theme.objects.all()
		if theme:
			for all_theme in all_themes:
				all_theme.current = False
				all_theme.save()

			theme.current = True
			theme.save()
		return HttpResponse('1')

	return HttpResponse('', status = 500)


@csrf_exempt
def active(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	if request.method=='POST':
		pk = request.POST['pk']
		theme = Theme.objects.filter(pk = pk).first()
		all_themes = Theme.objects.all()
		if theme:
			for all_theme in all_themes:
				all_theme.active = False
				all_theme.save()

			theme.active = True
			theme.count = 180
			theme.save()
		return HttpResponse('1')

	return HttpResponse('', status = 500)


@csrf_exempt
def deactive(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	if request.method=='POST':
		pk = request.POST['pk']
		theme = Theme.objects.filter(pk = pk).first()
		all_themes = Theme.objects.all()
		if theme:
			for all_theme in all_themes:
				all_theme.active = False
				all_theme.save()
		return HttpResponse('1')

	return HttpResponse('', status = 500)


def get_data(request):
	if not request.user.is_authenticated:
		return HttpResponse('', status = 500)

	if not request.user.profile.admin_access:
		return HttpResponse('', status = 500)

	theme = Theme.objects.filter(current = True).first()
	if theme:
		if theme.active:
			if theme.count > 0:
				theme.count -= 1
				theme.save()
			else:
				theme.active = False
				theme.save()

		data = {}
		current_site = get_current_site(request)
		protocol = 'http'
		if request.is_secure():
			protocol = 'https'


		data['theme_token'] = theme.theme_token
		data['url'] = protocol + '://' + current_site.domain + '/vote/' + theme.theme_token
		data['active'] = theme.active
		data['zoom'] = theme.zoom

		if theme.active:
			data['seconds'] = int(theme.count)
		else:
			data['seconds'] = 180
		vote_counts = {}
		vote_parts = VotePart.objects.filter(theme = theme)
		for vote_part in vote_parts:
			vote_counts[vote_part.pk] = VoteCount.objects.filter(vote_part = vote_part).count()

		data['vote_counts'] = vote_counts

		return HttpResponse(json.dumps(data))
	return HttpResponse('', status = 500)

