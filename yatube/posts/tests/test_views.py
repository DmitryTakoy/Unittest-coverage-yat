from django import forms
from django.test import TestCase, Client, override_settings
from posts.models import Group, Post, User, Follow
from django.urls import reverse
from django.core.cache import cache
import tempfile
import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hasnoname')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
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
        cls.group_sec = Group.objects.create(
            title='kot',
            slug='kot',
            description='kotik',
        )

    def check_post_on_page(self, response):
        try:
            x = response.context['page_obj'][0]
            return x
        except BaseException:
            i = False
            return i

    def creating_test_user(self):
        test_user = User.objects.create(
            username='Hasname',
        )
        return test_user

    def asserts_check_post(self, clas, obj):
        check_author = obj.author.username
        check_text = obj.text
        check_group = obj.group.slug
        self.assertEqual(check_author, 'hasnoname')
        self.assertEqual(check_text, 'Тестовый пост')
        self.assertEqual(check_group, 'pot')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

    def test_views_get_right_pages(self):
        """Проверяем: posts.view вызывает корректные шаблоны."""
        templates = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.post.author}): 'posts/profile.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.post.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id}): 'posts/create_post.html',
        }
        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_form_show_correct_context(self):
        """Проверяем: передается правильный контекст."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_list_page_shows_correct(self):
        """Проверяем group_list с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        first_object = self.check_post_on_page(response)
        self.asserts_check_post(self, first_object)

    def test_index_page_shows_correct(self):
        """Проверяем index с правильным содержимым"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = self.check_post_on_page(response)
        self.asserts_check_post(self, first_object)

    def test_post_by_user_id_page_shows_correct(self):
        """Проверяем profile с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_created_post_added(self):
        """Проверяем отображение поста на странице группы, автора, главной."""
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        group_object = self.check_post_on_page(response_group)
        profile_object = self.check_post_on_page(response_profile)
        index_object = self.check_post_on_page(response_index)
        self.asserts_check_post(self, group_object)
        self.asserts_check_post(self, profile_object)
        self.asserts_check_post(self, index_object)

    def test_created_post_not_added_to_other_group_page(self):
        """Проверяем: пост не отражается на странице другой группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_sec.slug}))
        self.assertNotContains(response, self.post)

    def test_comment_by_guest(self):
        """Проверяем комментирование неавториз. юзером."""
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': 0}))
        self.assertEqual(response.status_code, 302)

    def test_index_cache(self):
        """Проверяем работу кеширования."""
        # Cоздаем посты
        test_post = Post.objects.create(
            author=self.user,
            text='TeccccTb',
            group=self.group,
            image=None,
        )
        test_post_o = Post.objects.create(
            author=self.user,
            text='TeccccTb',
            group=self.group,
            image=None,
        )
        test_post_s = Post.objects.create(
            author=self.user,
            text='TeccccTb',
            group=self.group,
            image=None,
        )
        cache.clear()
        # Запрашиваю текущий вид главной страницы
        response = self.authorized_client.get(reverse('posts:index'))
        cache_mine = response.content
        # Удаляю посты
        test_post.delete()
        test_post_o.delete()
        test_post_s.delete()
        # Запрошу тек-й вид глав стр
        response_sec = self.authorized_client.get(reverse('posts:index'))
        # Сравню, что страницы одинаковы, несмотря на удаление постов
        self.assertEqual(cache_mine, response_sec.content)
        # Очищаю кеш, в кот были удаленные посты
        cache.clear()
        # Запрошу тек-й вид глав стр
        response_third = self.authorized_client.get(reverse('posts:index'))
        # Сравню кеш, в кот были удаленные посты и новый вид глав стр
        self.assertNotEqual(cache_mine, response_third.content)

    def test_image_shown_index(self):
        """Проверяем вывод изображения на основной стр."""
        # Cоздаем посты
        con = self.uploaded
        test_post = Post.objects.create(
            author=self.user,
            text='FIRST_TeccccTb',
            group=self.group,
            image=con,
        )
        # Запрашиваю индекс
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}))
        response_pd = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': test_post.id})
        )
        # Вытягиваю поле image
        first_object_on_index = self.check_post_on_page(response_index)
        first_object_on_profile = self.check_post_on_page(response_profile)
        first_object_on_group = self.check_post_on_page(response_group)
        obj_on_pd = response_pd.context['post']
        post_image_i = first_object_on_index.image
        post_image_pro = first_object_on_profile.image
        post_image_g = first_object_on_group.image
        post_image_pd = obj_on_pd.image
        self.assertEqual(post_image_i, f'posts/{con.name}')
        self.assertEqual(post_image_pro.name, f'posts/{con.name}')
        self.assertEqual(post_image_g.name, f'posts/{con.name}')
        self.assertEqual(post_image_pd.name, f'posts/{con.name}')

    def test_view_follow_works(self):
        """Проверяем подписка создает запись в базе."""
        test_user = self.creating_test_user()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': test_user.username}))
        checker = Follow.objects.filter(user=1, author=2).exists()
        self.assertTrue(checker)

    def test_view_unfollow_works(self):
        """Проверяем отписка удаляет запись в базе."""
        test_user = self.creating_test_user()
        Follow.objects.create(
            user=self.user,
            author=test_user,
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': test_user.username}))
        checker = Follow.objects.filter(user=1, author=2).exists()
        self.assertFalse(checker)

    def test_post_appear(self):
        """Проверяем пост появляется в ленте."""
        test_user = self.creating_test_user()
        test_post = Post.objects.create(
            author=test_user,
            text='new services check',
            group=self.group,
            image=None,
        )
        Follow.objects.create(
            user=self.user,
            author=test_user,
        )
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        object_on_page = self.check_post_on_page(response_follow)
        self.assertEqual(test_post.text, object_on_page.text)

    def test_post_appear(self):
        """Проверяем пост не отражается в ленте."""
        test_user = self.creating_test_user()
        Post.objects.create(
            author=test_user,
            text='new services check',
            group=self.group,
            image=None,
        )
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        object_on_page = self.check_post_on_page(response_follow)
        self.assertFalse(object_on_page, 'На странице есть пост')

    @classmethod
    def tearDownClass(cls) -> None:
        print(tempfile.mkdtemp)
        shutil.rmtree(settings.MEDIA_ROOT)
        return super().tearDownClass()
