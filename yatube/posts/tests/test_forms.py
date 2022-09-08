from http import HTTPStatus
from django.test import TestCase
from posts.forms import PostForm
from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase
from django.urls import reverse


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hasnoname')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='pot',
            slug='pot',
            description='potny',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_text_label(self):
        """Проверка labels."""
        text_label = PostFormTests.form.fields['text'].label
        group_label = PostFormTests.form.fields['group'].label
        self.assertEqual(text_label, 'Текст поста')
        self.assertEqual(group_label, 'Группа')

    def test_group_label(self):
        """Проверка help_texts."""
        help_text_text = PostFormTests.form.fields['text'].help_text
        help_text_group = PostFormTests.form.fields['group'].help_text
        self.assertEqual(help_text_text, 'Что хотите написать?')
        self.assertEqual(help_text_group, 'Относится к группе ?')

    def test_create_post(self):
        """Валидная форма создаёт запись в Post."""
        posts_count = Post.objects.count()
        one_more = 1
        form_data = {
            'text': 'testovy teeeekst',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse(
                                 'posts:profile', kwargs={
                                     'username': self.user.username}))
        self.assertEqual(Post.objects.count(), (posts_count + one_more))
        self.assertEqual(
            form_data['text'], Post.objects.latest('pub_date').text
        )

    def test_edit_post(self):
        """Валидная форма меняет содержание поля text."""
        form_data = {
            'text': 'testovy teeeekst25',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertEqual(
            form_data['text'], Post.objects.latest('pub_date').text)

    def test_comment_added_to_post_page(self):
        """Проверяем добавление комм. на пост и redirect."""
        form_data = {
            'text': 'testovy teeeekst',
            # 'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             reverse(
                                 'posts:post_detail', kwargs={
                                     'post_id': self.post.pk}))
        self.assertEqual(
            form_data['text'], Comment.objects.latest('pub_date').text
        )
