import os
from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(d, key):
	try:
		t = d[key]
	except:
		return None

	return t


@register.filter(name='filename')
def filename(d):
	return os.path.basename(d.file.name)


@register.filter(name='times') 
def times(number):
    return range(number)