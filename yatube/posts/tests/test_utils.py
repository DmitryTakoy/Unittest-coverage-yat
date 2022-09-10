from django.test import TestCase, Client
from posts.models import Group, Post
from django.urls import reverse
from posts.models import User
from django.core.cache import cache

Q_ON_PAGE_F = 10
Q_ON_PAGE_S = 4
Quant_OF_POST = 13


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
        obj = [
            Post(
                author=cls.user,
                text=f"Тесты_{i}",
                group=cls.group) for i in range(13)]
        Post.objects.bulk_create(objs=obj, batch_size=Quant_OF_POST)

    def test_first_page_paginator(self):
        """Проверем работу паджинатора на первой странице."""
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), Q_ON_PAGE_F)

    def test_sec_page_paginator(self):
        """Проверем работу паджинатора на второй странице."""
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), Q_ON_PAGE_S)

    def test_profile_page_paginator(self):
        """Проверем работу паджинатора на странице пользователя."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}))
        self.assertEqual(len(response.context['page_obj']), Q_ON_PAGE_F)

    def test_group_page_paginator(self):
        """Проверем работу паджинатора на странице групп."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}))
        self.assertEqual(len(response.context['page_obj']), Q_ON_PAGE_F)
