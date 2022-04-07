from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, Profile

User = get_user_model()


class PostModelTests(TestCase):
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
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
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
        cls.profile = Profile.objects.create(
            user=cls.author,
        )
        cls.expected_object_names = {
            cls.post.text[:15]: str(cls.post),
            cls.group.title: str(cls.group),
            cls.comment.text[:15]: str(cls.comment),
            f'{cls.follow.user.username} follower of '
            f'{cls.follow.author.username}': str(cls.follow),
            f'{cls.profile.user.username} profile': str(cls.profile),
        }

    def test_str_models_names(self):
        """В поле __str__ объекта модели записано ожидаемое значение."""
        for name, expected_object_name in self.expected_object_names.items():
            with self.subTest(name=name):
                self.assertEqual(name, expected_object_name)

    def test_post_verboses_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'pub_date': 'Дата публикации',
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)


class GroupModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='ж' * 100,
            description='Тестовое описание',
        )

    def test_text_convert_to_slug(self):
        """Содержимое поля title преобразуется в slug."""
        slug = self.group.slug
        self.assertEqual(slug, 'zh' * 50)

    def test_text_slug_max_length_not_exceed(self):
        """Длинный slug обрезается и не превышает max_length поля slug в модели.
        """
        max_length_slug = self.group._meta.get_field('slug').max_length
        length_slug = len(self.group.slug)
        self.assertEqual(max_length_slug, length_slug)
