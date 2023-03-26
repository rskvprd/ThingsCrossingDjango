from django.contrib import admin
from django.apps import apps

from ThingsCrossing.models import *

admin.site.register(Advertisement)
admin.site.register(Characteristic)
admin.site.register(Exchange)
admin.site.register(Picture)
admin.site.register(Price)

