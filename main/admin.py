from django.contrib import admin
from main.models import *
from parler.admin import TranslatableAdmin
# Register your models here.

admin.site.register(Player)
admin.site.register(User)
admin.site.register(Game)
admin.site.register(ChatMessage)
admin.site.register(Rank, TranslatableAdmin)
admin.site.register(Achievement, TranslatableAdmin)