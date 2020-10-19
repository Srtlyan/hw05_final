from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Class for group data.

    Stores group title, description and unique slug.
    """
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        )
    slug = models.SlugField(
        unique=True,
        verbose_name="slug",
        )
    description = models.TextField(
        verbose_name="Описание",
        )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Class for Post data.

    Stores post text, date of publication, author
    and belonging to a group (optional attribute).
    """
    class Meta:
        """Stores meta parameters for ordering objects by date"""

        ordering = ('-pub_date',)  # Ordering by publication date.
    text = models.TextField(
        verbose_name="Текст",
        )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        )
    group = models.ForeignKey(
        Group,
        related_name="posts",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Группа",
        )

    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name="Заглавная картинка"
        )

    def __str__(self):
        self.short_text = self.text[:15]
        return (
            f'Автор: {self.author}'
            f', Текст: "{self.short_text}..."'
            f', Дата: {self.pub_date}'
            f', Группа: {self.group}'
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
        )
    text = models.TextField(
        verbose_name="Текст комментария",
        )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации комментария",
        )


class Follow(models.Model):
    """Class for followers data.

    Stores group pairs of follower and following users.

    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчики",
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Авторы",
        )

    class Meta:
        """Stores unique pairs user-author"""
        unique_together = ('user', 'author')
