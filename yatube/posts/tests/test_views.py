from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django import forms
from posts.models import Comment, Follow, Group, Post
from posts.forms import CommentForm, PostForm
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.following_post = Post.objects.create(
            text='Пост для подписки',
            author=cls.not_author,
        )
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
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            post=cls.post,
            text='Тестовый коммент',
        )
        cls.follow = Follow.objects.create(
            user=cls.author,
            author=cls.not_author
        )
        cls.DIR_UPLOAD_TO = cls.post._meta.get_field('image').upload_to
        cls.name_kwargs_template = {
            'index': ('posts:index', None, 'posts/index.html'),
            'group_list': (
                'posts:group_list',
                {'url': cls.group.slug},
                'posts/group_list.html'
            ),
            'profile': (
                'posts:profile',
                {'username': cls.author},
                'posts/profile.html'
            ),
            'detail': (
                'posts:post_detail',
                {'post_id': cls.post.id},
                'posts/post_detail.html'
            ),
            'create': ('posts:post_create', None, 'posts/create_post.html'),
            'edit': (
                'posts:post_edit',
                {'post_id': cls.post.id},
                'posts/create_post.html'
            ),
            'follow': ('posts:follow_index', None, 'posts/follow.html'),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def check_post_obj_in_context(self, response):
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'][0], Post)

    def check_post_of_post_obj_is_correct(self, response):
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(
            first_object.author.username, self.post.author.username
        )
        self.assertEqual(first_object.group.title, self.post.group.title)
        self.assertEqual(
            first_object.image, f'{self.DIR_UPLOAD_TO}{self.uploaded}'
        )

    def check_PostForm_in_context(self, response):
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_pages_uses_correct_templates(self):
        """namespace:name использует соответствующий шаблон."""
        for page in self.name_kwargs_template:
            viewname, kwargs, template, = self.name_kwargs_template[page]
            with self.subTest(template=template):
                reverse_name = reverse(viewname, kwargs=kwargs)
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        viewname, _, _, = self.name_kwargs_template['index']
        response = self.author_client.get(reverse(viewname))
        PagesViewsTests.check_post_obj_in_context(self, response)
        PagesViewsTests.check_post_of_post_obj_is_correct(self, response)
        self.assertIn('keyword', response.context)
        self.assertIsNone(response.context['keyword'])

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        viewname, kwargs, _, = self.name_kwargs_template['group_list']
        response = self.author_client.get(reverse(viewname, kwargs=kwargs))
        PagesViewsTests.check_post_obj_in_context(self, response)
        PagesViewsTests.check_post_of_post_obj_is_correct(self, response)
        self.assertIn('group', response.context)
        self.assertEqual(
            response.context['group'].title, self.post.group.title
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        viewname, kwargs, _, = self.name_kwargs_template['profile']
        response = self.author_client.get(reverse(viewname, kwargs=kwargs))
        PagesViewsTests.check_post_obj_in_context(self, response)
        PagesViewsTests.check_post_of_post_obj_is_correct(self, response)
        self.assertIn('author', response.context)
        self.assertEqual(
            response.context['author'].username, self.post.author.username
        )
        self.assertIn('count', response.context)
        self.assertEqual(response.context['count'], 1)
        self.assertIn('following', response.context)
        self.assertFalse(response.context['following'])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        viewname, kwargs, _, = self.name_kwargs_template['detail']
        response = self.author_client.get(reverse(viewname, kwargs=kwargs))
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].author.username,
            self.post.author.username
        )
        self.assertEqual(
            response.context['post'].group.title,
            self.post.group.title
        )
        self.assertEqual(
            response.context['post'].image,
            f'{self.DIR_UPLOAD_TO}{self.uploaded}'
        )
        self.assertIn('user', response.context)
        self.assertEqual(
            response.context['user'].username,
            self.post.author.username
        )
        self.assertIn('count', response.context)
        self.assertEqual(response.context['count'], 1)
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'][0], self.comment)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_post_create_page_show_correct_context(self):
        """Шаблон create_post.html сформирован с правильным контекстом."""
        viewname, _, _, = self.name_kwargs_template['create']
        response = self.author_client.get(reverse(viewname))
        PagesViewsTests.check_PostForm_in_context(self, response)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post.html для edit сформирован с правильным
        контекстом."""
        viewname, kwargs, _, = self.name_kwargs_template['edit']
        response = self.author_client.get(reverse(viewname, kwargs=kwargs))
        PagesViewsTests.check_PostForm_in_context(self, response)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertIn('post_id', response.context)
        self.assertEqual(response.context['post_id'], self.post.id)
        self.assertIn('is_edit', response.context)
        self.assertTrue(response.context['is_edit'])

    def test_follow_page_show_correct_context(self):
        """Шаблон follow.html сформирован с правильным контекстом."""
        viewname, _, _, = self.name_kwargs_template['follow']
        response = self.author_client.get(reverse(viewname))
        PagesViewsTests.check_post_obj_in_context(self, response)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.following_post.text)
        self.assertEqual(
            first_object.author.username, self.not_author.username
        )

    def test_cache(self):
        """Главная страница сайта кеширует содержимое на 20 секунд"""
        viewname, _, _, = self.name_kwargs_template['index']
        response = self.client.get(reverse(viewname))
        self.assertNotIn(
            'Тестирование cache', response.content.decode('utf-8')
        )
        Post.objects.create(
            text='Тестирование cache',
            author=self.author,
            group=self.group,
        )
        response = self.client.get(reverse(viewname))
        self.assertNotIn(
            'Тестирование cache', response.content.decode('utf-8')
        )
        cache.clear()  # time.sleep(20)
        response = self.client.get(reverse(viewname))
        self.assertIn(
            'Тестирование cache', response.content.decode('utf-8')
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.follow = Follow.objects.create(
            user=cls.not_author,
            author=cls.author
        )
        post_list = list()
        POSTS_TWO_PAGES = 13
        POSTS_FIRST_PAGE = 10
        POSTS_SECOND_PAGE = 3
        for i in range(POSTS_TWO_PAGES):
            post_list.append(
                Post(
                    text='Тестовый пост ' + str(i),
                    author=cls.author,
                    group=cls.group
                )
            )
        Post.objects.bulk_create(post_list)
        cls.posts_on_pages = {
            reverse('posts:index'): POSTS_FIRST_PAGE,
            reverse('posts:index') + '?page=2': POSTS_SECOND_PAGE,
            reverse(
                'posts:group_list', kwargs={'url': cls.group.slug}
            ): POSTS_FIRST_PAGE,
            reverse(
                'posts:group_list', kwargs={'url': cls.group.slug}
            ) + '?page=2': POSTS_SECOND_PAGE,
            reverse(
                'posts:profile', kwargs={'username': cls.author}
            ): POSTS_FIRST_PAGE,
            reverse(
                'posts:profile', kwargs={'username': cls.author}
            ) + '?page=2': POSTS_SECOND_PAGE,
        }
        cls.posts_on_follow = {
            reverse('posts:follow_index'): POSTS_FIRST_PAGE,
            reverse('posts:follow_index') + '?page=2': POSTS_SECOND_PAGE,
        }

    def setUp(self):
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_pages_contains_ten_three_posts(self):
        """Проверяем, что количество постов на 1й странице 10,
        а на второй - 3"""
        for reverse_name, posts_on_page in self.posts_on_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                PagesViewsTests.check_post_obj_in_context(self, response)
                count_posts = len(response.context['page_obj'])
                self.assertEqual(count_posts, posts_on_page)
        for reverse_name, posts_on_page in self.posts_on_follow.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.not_author_client.get(reverse_name)


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group_1,
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        Post.objects.create(
            text='Тестовый пост 2',
            author=cls.author,
            group=cls.group_2,
        )
        cls.name_kwargs = {
            'posts:index': None,
            'posts:group_list': {'url': cls.group_1.slug},
            'posts:profile': {'username': cls.author},
        }

    def test_post_on_pages_groups(self):
        """Проверяем, что пост появляется на главной странице,
        на странице выбранной группы, в профайле пользователя,
        и не появляется на странице другой группы"""
        for name in self.name_kwargs:
            response = self.client.get(
                reverse(name, kwargs=self.name_kwargs[name])
            )
            with self.subTest(response=response):
                PagesViewsTests.check_post_obj_in_context(self, response)
                self.assertIn(self.post, response.context['page_obj'])
        response = self.client.get(
            reverse('posts:group_list', kwargs={'url': self.group_2.slug})
        )
        PagesViewsTests.check_post_obj_in_context(self, response)
        self.assertNotIn(self.post, response.context['page_obj'])


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.subscriber = User.objects.create_user(username='Subscriber')
        cls.unsubscriber = User.objects.create_user(username='NotSubscriber')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )

    def setUp(self):
        self.subscriber_client = Client()
        self.subscriber_client.force_login(self.subscriber)
        self.unsubscriber_client = Client()
        self.unsubscriber_client.force_login(self.unsubscriber)

    def test_follow_for_user(self):
        """Залогиненный пользователь может подписываться на других авторов"""
        follows_count = Follow.objects.count()
        self.assertFalse(
            Follow.objects.filter(
                user=self.subscriber,
                author=self.author
            ).exists()
        )
        response = self.subscriber_client.post(
            reverse('posts:profile_follow', args=(self.author.username,)),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.author.username,))
        )
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.subscriber,
                author=self.author
            ).exists()
        )

    def test_unfollow_for_user(self):
        """Залогиненный пользователь может отписываться от других авторов"""
        Follow.objects.create(
            user=self.subscriber,
            author=self.author
        )
        follows_count = Follow.objects.count()
        self.assertTrue(
            Follow.objects.filter(
                user=self.subscriber,
                author=self.author
            ).exists()
        )
        response = self.subscriber_client.post(
            reverse('posts:profile_unfollow', args=(self.author.username,)),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.author.username,))
        )
        self.assertEqual(Follow.objects.count(), follows_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.subscriber,
                author=self.author
            ).exists()
        )

    def test_post_shows_for_subscriber(self):
        """Новая запись автора появляется в ленте подписчиков."""
        response = self.subscriber_client.post(
            reverse('posts:profile_follow', args=(self.author.username,)),
            follow=True
        )
        new_post = Post.objects.create(
            text='Новый пост автора',
            author=self.author,
        )
        response = self.subscriber_client.get(reverse('posts:follow_index'))
        PagesViewsTests.check_post_obj_in_context(self, response)
        self.assertIn(new_post, response.context['page_obj'])
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Новый пост автора')
        self.assertEqual(
            first_object.author.username, self.post.author.username
        )

    def test_post_not_shows_for_unsubscriber(self):
        """Новая запись автора не появляется в ленте не подписчиков."""
        response = self.unsubscriber_client.post(
            reverse('posts:profile_unfollow', args=(self.author.username,)),
            follow=True
        )
        new_post = Post.objects.create(
            text='Новый пост автора',
            author=self.author,
        )
        response = self.unsubscriber_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn('page_obj', response.context)
        self.assertNotIn(new_post, response.context['page_obj'])
        self.assertNotIn(
            self.post.text, response.content.decode('utf-8')
        )

        self.assertNotIn(
            'Новый пост автора', response.content.decode('utf-8')
        )
