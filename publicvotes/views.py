import os
import datetime

from datetime import date
from django.http import HttpResponse

from django.conf import settings
from django.core.files.storage import default_storage

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from .models import Theme, VotePart, VoteCount
from .forms import ThemeForm, VotePartForm


@login_required(login_url='/login/')
def view_themes(request):
	if not request.user.profile.admin_access:
		return redirect ('home')

	themes = Theme.objects.all().order_by('number')

	args = {
		'menu': 'blocks',
		'themes': themes
	}
	return render(request, 'publicvotes/view_themes.html', args)


@login_required(login_url='/login/')
def delete_theme(request, pk = None):
	if not request.user.profile.admin_access or not pk:
		return redirect('home')

	Theme.objects.filter(pk = pk).delete()
	return redirect('publicvotes:themes')


@login_required(login_url='/login/')
def add_theme(request):
	if not request.user.profile.admin_access:
		return redirect('home')

	if request.method=='POST':
		form = ThemeForm(request.POST, label_suffix='')
		if form.is_valid():
			new_theme = form.save(False)
			new_theme.save()

			return redirect('publicvotes:themes')
			
		args = {
			'menu': 'blocks',
			'form': form
		}
		return render(request, 'publicvotes/add_theme.html', args)

	form = ThemeForm(label_suffix='')
	args = {
		'menu': 'blocks',
		'form': form
	}
	return render(request, 'publicvotes/add_theme.html', args)


@login_required(login_url='/login/')
def edit_theme(request, pk = None):
	if not request.user.profile.admin_access:
		return redirect('home')

	theme = Theme.objects.filter(pk = pk).first()
	if not theme:
		return redirect('publicvotes:themes')

	if request.method=='POST':
		form = ThemeForm(request.POST, instance=theme, label_suffix='')

		if form.is_valid():
			theme_form = form.save(False)
			theme_form.save()	

			return redirect('publicvotes:themes')

		args = {
			'menu': 'blocks',
			'theme': theme,
			'form': form,
		}
		return render(request, 'publicvotes/edit_theme.html', args)


	form = ThemeForm(instance=theme, label_suffix='')

	args = {
		'menu': 'blocks',
		'theme': theme,
		'form': form,
	}
	return render(request, 'publicvotes/edit_theme.html', args)

########################################################################
@login_required(login_url='/login/')
def view_voteparts(request):
	if not request.user.profile.admin_access:
		return redirect ('home')

	voteparts = VotePart.objects.all().order_by('theme__number', 'number')

	args = {
		'menu': 'subblocks',
		'voteparts': voteparts
	}
	return render(request, 'publicvotes/view_voteparts.html', args)


@login_required(login_url='/login/')
def delete_votepart(request, pk = None):
	if not request.user.profile.admin_access or not pk:
		return redirect('home')

	VotePart.objects.filter(pk = pk).delete()
	return redirect('publicvotes:view_voteparts')


@login_required(login_url='/login/')
def add_votepart(request):
	if not request.user.profile.admin_access:
		return redirect('home')

	if request.method=='POST':
		form = VotePartForm(request.POST, label_suffix='')
		if form.is_valid():
			new_votepart = form.save(False)
			new_votepart.save()

			return redirect('publicvotes:voteparts')
			
		args = {
			'menu': 'subblocks',
			'form': form
		}
		return render(request, 'publicvotes/add_votepart.html', args)

	form = VotePartForm(label_suffix='')
	args = {
		'menu': 'subblocks',
		'form': form
	}
	return render(request, 'publicvotes/add_votepart.html', args)


@login_required(login_url='/login/')
def edit_votepart(request, pk = None):
	if not request.user.profile.admin_access:
		return redirect('home')

	votepart = VotePart.objects.filter(pk = pk).first()
	if not votepart:
		return redirect('publicvotes:voteparts')

	if request.method=='POST':
		form = VotePartForm(request.POST, instance=votepart, label_suffix='')

		if form.is_valid():
			votepart_form = form.save(False)
			votepart_form.save()	

			return redirect('publicvotes:voteparts')

		args = {
			'menu': 'subblocks',
			'votepart': votepart,
			'form': form,
		}
		return render(request, 'publicvotes/edit_votepart.html', args)


	form = VotePartForm(instance=votepart, label_suffix='')

	args = {
		'menu': 'subblocks',
		'votepart': votepart,
		'form': form,
	}
	return render(request, 'publicvotes/edit_votepart.html', args)


@csrf_exempt
def add_vote(request):
	if not request.session.session_key:
		request.session.create()
	session_token = request.session.session_key

	if request.method=='POST':
		pk = request.POST['pk']
		votepart = VotePart.objects.filter(pk = pk).first()
		if votepart:
			vote_count = VoteCount.objects.filter(session_token = session_token, vote_part = votepart).first()
			if not vote_count:
			
				VoteCount.objects.create(session_token = session_token, vote_part = votepart)
	return HttpResponse('1')