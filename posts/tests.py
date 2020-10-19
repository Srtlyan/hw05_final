from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import Follow, Group, Post


class YatubeTest(TestCase):
    def setUp(self):
        '''Set data for test.

        Create main test user.
        Create post.
        Create another test user.
        Stores reverse page functions.
        '''
        self.test_username = 'sarah'
        self.test_username_2 = 'john'
        self.test_password = '12345'
        self.test_text = 'wjgocnugvwhjkrghwuy5t4f65gf2ydgsydygdbwdhbgu5ccg'
        self.test_text_2 = '3ci5tf2n8dhg2b62fbtwgcnh48g5dgwdi gu3f tqdybwd'
        self.test_comment = 'gwwgmy5gv4u5fgygehnyh5gugghdygbeuy5uvgdtegu45'
        self.img = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('./media/test_img/test_image.jpg', 'rb').read(),
            content_type='image/jpeg',
            )
        self.client_authorized = Client()
        self.client_authorized_2 = Client()
        self.client_unauthorized = Client()
        self.test_group = Group.objects.create(
            title='test-group',
            slug='test-group',
            )
        self.user = User.objects.create(
                        username=self.test_username,
                        password=self.test_password,
                        )
        self.user_2 = User.objects.create(
                        username=self.test_username_2,
                        password=self.test_password,
                        )
        self.post = Post.objects.create(
            text=self.test_text,
            author=self.user,
            )
        self.client_authorized.force_login(self.user)
        self.client_authorized_2.force_login(self.user_2)

        self.reverse_index = reverse(
            'index',
            )
        self.reverse_profile = reverse(
            'profile',
            args=[self.user.username],
            )
        self.reverse_post = reverse(
            'post',
            args=[self.user.username, self.post.id],
            )
        self.reverse_new_post = reverse(
            'new_post',
            )
        self.reverse_post_edit = reverse(
            'post_edit',
            args=[self.user.username, self.post.id],
            )
        self.reverse_follow = reverse(
            'follow_index',
            )
        self.reverse_add_comment = reverse(
            'add_comment',
            args=[self.user.username, self.post.id],
            )

    def post_display(self, url, text, message):
        '''Check if test text and text on provided urls are equal.'''
        response = self.client_authorized.get(url)
        self.assertIn(
            text,
            response.context['post'].text,
            msg=message
            )

    def server_status(self, client, url, status_code, message):
        response = client.get(url)
        self.assertEqual(
            response.status_code,
            status_code,
            msg=message,
            )

    def text_not_in_DB(self, text, message):
        '''Check if test text is not in DB.'''
        self.assertNotIn(
            text,
            Post.objects.get().text,
            msg=message,
            )

    def test_profile(self):
        '''Check user profile page.

        Check that status code of the user profile page is 200.
        Check that the user registered in DB.
        '''
        self.server_status(
            self.client_authorized,
            self.reverse_profile,
            200,
            'Status code of the user profile page is 200.',
            )

        self.assertEqual(
            self.user,
            User.objects.get(username=self.test_username),
            msg='The user registered in DB.',
            )

    def test_new_post(self):
        '''Check that authorized user can create a new post.

        Check that the new post appears on index page.
        Check that the new post text registered in DB.
        '''
        self.client_authorized.post(
            self.reverse_new_post,
            {'text': self.test_text_2},
            )
        cache.clear()
        self.post_display(
            self.reverse_index,
            self.test_text_2,
            'New post appears on index page.',
            )
        self.assertEqual(
            self.test_text_2,
            Post.objects.get(text=self.test_text_2).text,
            msg='The new post text registered in DB.',
            )

    def test_new_post_unauthorized(self):
        '''Check that unauthorized user can't create a new post.

        Check that unauthorized user redirected to login page.
        Check that new post is not appears on index page.
        Check that the new post text not registered in DB.
        '''
        response = self.client_unauthorized.get(self.reverse_new_post)
        self.assertRedirects(
            response,
            '/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200,
            msg_prefix='Unauthorized user redirected to login page',
            )
        self.client_unauthorized.post(
            self.reverse_new_post,
            {'text': self.test_text_2},
            )
        self.text_not_in_DB(
            self.test_text_2,
            'The new post text not registered in DB.',
            )

    def test_new_post_display(self):
        '''Check that post appears on related pages.

        Check index page.
        Check profile page.
        Check post page.
        '''
        urls = [
            self.reverse_index,
            self.reverse_profile,
            self.reverse_post,
            ]
        for url in urls:
            cache.clear()
            self.post_display(
                url,
                self.test_text,
                'post appears on related page',
                )

    def test_post_edit_author(self):
        '''Check that post author can post edit own post.

        Check that post text have been edited.
        '''
        self.client_authorized.post(
            self.reverse_post_edit,
            {'text': self.test_text_2},
            )
        self.post_display(
            self.reverse_post,
            self.test_text_2,
            'Post text have been edited',
            )

    def test_post_edit_unauthorized(self):
        '''Check that unauthorized user can not edit post.

        Check that the edited post have not changed in DB.
        '''
        self.client_unauthorized.post(
            self.reverse_post_edit,
            {'text': self.test_text_2},
            )
        self.text_not_in_DB(
            self.test_text_2,
            'The edited post text have not changed in DB.',
            )

    def test_post_edit_not_author(self):
        '''Check that authorized user, but not an author can not edit post.

        Check that the edited post have not changed in DB.
        '''
        self.client_authorized_2.post(
            self.reverse_post_edit,
            {'text': self.test_text_2},
            )
        self.text_not_in_DB(
            self.test_text_2,
            'The edited post text have not changed in DB.',
            )

    def test_404_status(self):
        '''Check that server returns 404 page.'''
        response = self.client_authorized.get(
            reverse(
                'profile',
                args={'username': 'несущуствующий профиль'},
                ),
            )
        self.assertEqual(response.status_code, 404, msg='Status code is 404.')

    def test_cache_index(self):
        '''Check that index page has cache.'''
        self.client_authorized.post(
            self.reverse_post_edit,
            {'text': self.test_text_2},
            )

        cache.clear()
        response = self.client_authorized.get(self.reverse_index)
        self.assertIn(
            self.test_text_2,
            response.context['post'].text,
            msg='Текст изменен'
            )

    def test_follow_check(self):
        '''Check that user can follow/unfollow other users.'''
        response = self.client_authorized.get(
            reverse(
                'profile',
                args=[self.user_2],
                ),
            )
        self.assertContains(response, text='Подписаться')
        Follow.objects.create(user=self.user, author=self.user_2),
        response = self.client_authorized.get(
            reverse(
                'profile',
                args=[self.user_2],
                ),
            )
        self.assertContains(response, text='Отписаться')

    def test_follow_index(self):
        '''Check that post appears on follow page only if user is follower.'''
        response = self.client_authorized_2.get(self.reverse_follow)
        self.assertNotContains(response, self.post,)
        self.follow = Follow.objects.create(user=self.user_2, author=self.user)
        response = self.client_authorized_2.get(self.reverse_follow)
        self.assertContains(response, self.test_text)

    def test_add_comment_authorized(self):
        '''Check that authorized user can add comment to post.'''
        response = self.client_authorized.post(
            self.reverse_add_comment,
            {'text': self.test_comment},
            )
        self.assertContains(response, self.test_comment)

    def test_add_comment_unauthorized(self):
        '''Check that unauthorized user can not add comment to post.'''
        response = self.client_unauthorized.post(
            self.reverse_add_comment,
            {'text': self.test_comment},
            )
        self.assertEqual(
            response.status_code,
            302,
            msg='Unauthorized user can not add comment',
            )
