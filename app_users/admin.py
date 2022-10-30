from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy

from django.utils.html import format_html


class UserAdmin(admin.ModelAdmin):
    # exclude = ('photo',)
    readonly_fields = ("photo_media",)

    def photo_media(self, obj):
        # return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
        #     url=obj.photo.url, # once again, this is the name of the actual image field in your model
        #     width=obj.photo.width if obj.photo.width<150 else 300, # or define custom width
        #     height=obj.photo.height if obj.photo.height if < 150 else 150, # same as above
        #     ))
        return mark_safe(
            '<img src="{url}" width="{width}" height="{height}" />'.format(
                url=f"{reverse_lazy('view_picture')}?name={obj.photo.name}",  # once again, this is the name of the actual image field in your model
                height=obj.photo.width if obj.photo.width < 300 else 300,
                width=obj.photo.height
                if obj.photo.width < 300
                else int(obj.photo.height * 300 / obj.photo.width),
            )
        )
        # return mark_safe('<img src="{}" width="300" height="300" />'.format(obj.photo.url))


admin.site.register(User, UserAdmin)
