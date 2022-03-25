from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from posts.models import Comment, Group, Post
from posts.forms import PostForm
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.DIR_UPLOAD_TO = cls.post._meta.get_field('image').upload_to

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author = User.objects.create_user(username='NotAuthor')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый пост 2',
                author=self.author,
                group=self.group.id,
                image=f'{self.DIR_UPLOAD_TO}{self.uploaded}',
            ).exists()
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.author,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 2',
                author=self.author,
                group=self.group.id,
                image=f'{self.DIR_UPLOAD_TO}{self.uploaded}',
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый пост с изменениями',
                author=self.author,
                group=self.group.id,
            ).exists()
        )
        form_data = {
            'text': 'Тестовый пост с изменениями',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост с изменениями',
                author=self.author,
                group=self.group.id,
            ).exists()
        )

    def test_comment_create(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()
        self.assertFalse(
            Comment.objects.filter(
                text='Тестовый коммент',
                author=self.not_author,
                post=self.post.id,
            ).exists()
        )
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.not_author_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент',
                author=self.not_author,
                post=self.post.id,
            ).exists()
        )
