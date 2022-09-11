from http import HTTPStatus
from posts.models import Post, Group, User
from django.test import TestCase, Client
from django.urls import reverse


class PostsUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='hasnoname')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.usertwo = User.objects.create_user(username='hulk')
        cls.authorized_client_h = Client()
        cls.authorized_client_h.force_login(cls.usertwo)
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

    def test_views_able_to_auth_ed(self):
        """Проверяем: доступность privat страницы."""
        templates = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.post.author}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.post.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'users:logout'): HTTPStatus.OK,
        }
        for reverse_name, status_code in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)

    def test_views_able_to_guest(self):
        """Проверяем: public страницы."""
        templates = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.post.author}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.post.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'users:login'): HTTPStatus.OK,
            reverse(
                'users:signup'): HTTPStatus.OK,
        }
        for reverse_name, status_code in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                # Александр проверка для авторизованого
                # пользователя выше, тоже сабтестом.
                self.assertEqual(response.status_code, status_code)

    def test_post_create(self):
        """Страница cоздания поста перенавправляет guest-пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit(self):
        """Страница редакт-ия поста перенавправляет guest-пользователя."""
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_urls_auth_correct_template(self):
        """URL-адрес использует соответствующий шаблон для auth-ed."""
        random_name = 'Kendrick'
        templates_url_names = {
            '/': 'posts/index.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/{random_name}/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_correct_template(self):
        """URL-адрес использует соответствующий шаблон для guest."""
        templates_url_names = {
            '/': 'posts/index.html',
            # f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
