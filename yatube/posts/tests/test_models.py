from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from posts.models import Comment, Follow, Group, Post, Profile
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostModelTest(TestCase):
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

    def test_post_name_is_15_letters_of_text(self):
        """В поле __str__  объекта post записано значение поля post.text[:15].
        """
        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, str(self.post))

    def test_comment_name_is_15_letters_of_text(self):
        """В поле __str__  объекта comment записано значение поля comment.text[:15].
        """
        expected_object_name = self.comment.text[:15]
        self.assertEqual(expected_object_name, str(self.comment))

    def test_follow_name_is_user_follower_of_author(self):
        """В поле __str__  объекта follow записано значение
        user.username follower of author.username."""
        expected_object_name = (
            f'{self.follow.user.username} follower of '
            f'{self.follow.author.username}'
        )
        self.assertEqual(expected_object_name, str(self.follow))

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


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='ж' * 100,
            description='Тестовое описание',
        )

    def test_group_name_is_title_field(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProfileModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
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
        cls.profile = Profile.objects.create(
            user=cls.user,
            avatar=cls.uploaded,
        )
        cls.DIR_UPLOAD_TO = cls.profile._meta.get_field('avatar').upload_to

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_profile_name_is_username_field(self):
        """В поле __str__  объекта profile записано значение
        user.username profile.
        """
        expected_object_name = f'{self.profile.user.username} profile'
        self.assertEqual(expected_object_name, str(self.profile))

    def test_load_avatar_profile(self):
        """В базе присутсвует объект profile с аватаркой"""
        self.assertTrue(
            Profile.objects.filter(
                user=self.user,
                avatar=f'{self.DIR_UPLOAD_TO}{self.uploaded}'
            ).exists()
        )
