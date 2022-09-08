from django.test import TestCase
from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовй пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        exp = post.text
        self.assertEqual(exp, str(post))

    def test_verbose_name(self):
        """Проверяем verbose_name."""
        post = PostModelTest.post
        post_verbose_name = {
            'text': 'Текст',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Сообщество'
        }
        for field, value in post_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    value
                )

    def test_help_text(self):
        """help_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        post_help_text = {
            'text': 'Тееекст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, value in post_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    value
                )
