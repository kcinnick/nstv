from django.contrib import admin
from .models import Show, Episode, Movie, CastMember, NZBDownload

# Register your models here.
admin.site.register(Show)
admin.site.register(Episode)
admin.site.register(Movie)
admin.site.register(CastMember)
admin.site.register(NZBDownload)