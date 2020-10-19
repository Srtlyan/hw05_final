from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """Class that creating form for post."""
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image',
            )


class CommentForm(ModelForm):
    """Class that creating form for сomment."""
    class Meta:
        model = Comment
        fields = (
            'text',
            )
