from django.contrib import admin

from .models import Group, Post, Follow


class GroupAdmin(admin.ModelAdmin):
    """Admin model for Group class objects."""
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('pk', 'slug', 'title', 'description')


class PostAdmin(admin.ModelAdmin):
    """Admin model for Post class objects."""
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

class FollowAdmin(admin.ModelAdmin):
    """Admin model for Post class objects."""
    list_display = ('pk', 'user', 'author')
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
