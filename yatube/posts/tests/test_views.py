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


def check_post_on_page(response):
    return response.context['page_obj'][0]


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
        first_object = check_post_on_page(response)
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.slug
        self.assertEqual(post_author_0, 'hasnoname')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'pot')

    def test_index_page_shows_correct(self):
        """Проверяем index с правильным содержимым"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = check_post_on_page(response)
        self.assertEqual(first_object.author.username, 'hasnoname')
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.group.slug, 'pot')

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
        group_object = check_post_on_page(response_group)
        profile_object = check_post_on_page(response_profile)
        index_object = check_post_on_page(response_index)
        self.assertEqual(group_object.text, 'Тестовый пост')
        self.assertEqual(profile_object.text, 'Тестовый пост')
        self.assertEqual(index_object.text, 'Тестовый пост')

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

    def setUp(self) -> None:
        cache.clear()

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

    def test_image_shown_index(self):
        """Проверяем вывод изображения на основной стр."""
        # Cоздаем посты
        # image = Image.new('RGB', (100, 100))
        # image_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        # image.save(image_file)
        # cons = ContentFile(image_file)
        # con = BytesIO.getvalue(image_file)
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
        first_object_on_index = check_post_on_page(response_index)
        first_object_on_profile = check_post_on_page(response_profile)
        first_object_on_group = check_post_on_page(response_group)
        obj_on_pd = response_pd.context['post']
        post_image_i = first_object_on_index.image
        post_image_pro = first_object_on_profile.image
        post_image_g = first_object_on_group.image
        post_image_pd = obj_on_pd.image
        self.assertEqual(post_image_i, f'posts/{con.name}')
        self.assertEqual(post_image_pro.name, f'posts/{con.name}')
        self.assertEqual(post_image_g.name, f'posts/{con.name}')
        self.assertEqual(post_image_pd.name, f'posts/{con.name}')

    def test_auth_follow_delete(self):
        """Новый сервис подписки работает."""
        # Create User
        test_user = User.objects.create(
            username='Hasname',
        )
        test_post = Post.objects.create(
            author=test_user,
            text='new services check',
            group=self.group,
            image=None,
        )
        p = Follow.objects.create(
            user=self.user,
            author=test_user,
        )
        # Subscribe
        cache.clear()
        # Get Page with Fav Authors
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        response_follow_by_guest = self.guest_client.get(
            reverse('posts:follow_index'))
        # Check Follow_Page indicate post
        objects_on_page = check_post_on_page(response_follow).text
        objects_on_page_cont = response_follow.context
        # Check Follow_Page does not for guest
        objects_on_page_sec = response_follow_by_guest.context
        self.assertEqual(test_post.text, objects_on_page)
        self.assertNotEqual(objects_on_page_sec, objects_on_page_cont)
        # Compare Follow_Page when sub-ed and when not
        cache.clear()
        p.delete()
        response_follow_when_unfollowed = self.authorized_client.get(
            reverse('posts:follow_index'))
        objects_on_page_after_unsub = response_follow_when_unfollowed.context
        self.assertNotEqual(objects_on_page_after_unsub, objects_on_page_cont)

    def test_follow_view_works(self):
        """Подписка создает/удаляет запись в базе."""
        test_user = User.objects.create(
            username='Hasname',
        )
        # subscribe
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': test_user.username}))
        # check if appear
        checker = Follow.objects.filter(user=1, author=2).exists()
        self.assertTrue(checker)
        # unsub-be
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': test_user.username}))
        # check if deleted
        checker_sec = Follow.objects.filter(user=1, author=2).exists()
        self.assertFalse(checker_sec)

    @classmethod
    def tearDownClass(cls) -> None:
        print(tempfile.mkdtemp)
        shutil.rmtree(settings.MEDIA_ROOT)
        return super().tearDownClass()
