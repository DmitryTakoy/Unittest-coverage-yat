from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField(max_length=100)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст',
                            help_text='Тееекст')
    # pub_date = models.DateTimeField(auto_now_add=True,
    #                                verbose_name='Дата публикации',
    #                                help_text='Дата'
    #                                )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',
                               help_text='Автор'
                               )
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='groups',
                              verbose_name='Сообщество',
                              help_text='Группа'
                              )
    image = models.ImageField('Картинка',
                              upload_to='posts/',
                              blank=True,
                              )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             )
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE,
                               )
    text = models.TextField(verbose_name='комментарий')
    # created = models.DateTimeField(auto_now_add=True,
    #                               verbose_name='Дата публикации',
    #                               help_text='Дата',
    #                               )

    class Meta:
        ordering = ["-pub_date"]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)
