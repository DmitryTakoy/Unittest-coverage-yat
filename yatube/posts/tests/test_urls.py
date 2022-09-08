from posts.models import Post, Group, User
from django.test import TestCase, Client


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

    def test_index_page(self):
        """Проверяем доступность index."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        """Проверяем доступность страницы поста."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail_auth(self):
        """Проверяем доступность страницы поста для auth."""
        response = self.authorized_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_auth_login(self):
        """Проверяем доступность логина."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

    def test_auth_signup(self):
        """Проверяем доступность регистрации."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)

    def test_auth_signup(self):
        """ регистрации."""
        response = self.guest_client.get('/auth/signup/')
        self.assertNotEqual(response.status_code, 302)

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

    def test_group_list(self):
        """Проверяем доступность страницы с постами группы."""
        response = self.authorized_client.get(
            f'/group/{self.post.group.slug}/')
        self.assertEqual(response.status_code, 200)

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
