from django.contrib import admin
from .models import Theme, VotePart, VoteCount


admin.site.register({Theme, VotePart, VoteCount})
