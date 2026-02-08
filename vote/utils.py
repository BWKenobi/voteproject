import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from profileuser.models import Profile

def base_context(request):
	protocol = 'http://'
	if request.is_secure():
		protocol = 'https://'
	no_user = protocol + str(get_current_site(request)) + settings.STATIC_URL + 'img/no-user.jpg'
	no_image = protocol + str(get_current_site(request)) + settings.STATIC_URL + 'img/no-image.png'

	cookie_flag = True
	if "coockes" in request.session:
		cookie_flag = False
		if request.user.is_authenticated:
			if request.session['coockes'] == '1' and not request.user.profile.cookies_agree:
				request.user.profile.cookies_agree = True
				request.user.profile.save()

	else:
		if request.user.is_authenticated:
			if request.user.profile.cookies_agree:
				cookie_flag = False
				request.session['coockes'] = '1'

	args = {
		'cookie_flag': cookie_flag,
		'no_user': no_user,
		'no_image': no_image,
	}
	return args