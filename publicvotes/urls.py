from django.urls import path
from django.conf.urls import url

from .views import *

urlpatterns = [
	path('themes', view_themes, name = 'themes'),
	path('delete/<int:pk>', delete_theme, name = 'delete_theme'),
	path('add', add_theme, name = 'add_theme'),
	path('edit/<int:pk>', edit_theme, name = 'edit_theme'),

	path('voteparts', view_voteparts, name = 'voteparts'),
	path('delete_votepart/<int:pk>', delete_votepart, name = 'delete_votepart'),
	path('add_votepart', add_votepart, name = 'add_votepart'),
	path('edit_votepart/<int:pk>', edit_votepart, name = 'edit_votepart'),
]


urlpatterns += [
    path('ajax/add_vote', add_vote, name = 'ajax_add_vote'),
]
