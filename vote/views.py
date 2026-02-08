import datetime

from django.db.models import Q
from datetime import date

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
	
	for theme in themes:
		votepart_counts = {}
		voteparts= VotePart.objects.filter(theme = theme).order_by('number')
		for votepart in voteparts:
			votepart_counts[votepart] = VoteCount.objects.filter(vote_part = votepart).count()

		sorted_counts[theme.pk] =  dict(sorted(votepart_counts.items(), key=lambda x: x[1], reverse=True))


	args = {
		'themes': themes,
		'votepart_counts': votepart_counts,
		'sorted_counts': sorted_counts
	}

	return render(request, 'control_view.html', args)


@login_required(login_url='/login')
def concerted_view(request):
	if not request.user.profile.admin_access:
		return redirect ('home')

	return render(request, 'main_vote.html')


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

