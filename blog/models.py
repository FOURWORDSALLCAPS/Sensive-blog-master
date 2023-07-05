from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class TagQuerySet(models.QuerySet):

    def popular(self):
        tags_at_popular = self.annotate(Count('posts')).order_by('-posts__count')
        return tags_at_popular


class PostQuerySet(models.QuerySet):

    def popular(self):
        posts_at_popular = self.annotate(Count('likes')).order_by('-likes__count')
        return posts_at_popular

    def fetch_with_comments_count(self):
        most_popular_posts_ids = self.values_list('id', flat=True)
        comments_count = Comment.objects.filter(post_id__in=most_popular_posts_ids).values('post_id').annotate(
            comments_count=Count('id'))
        count_for_id = {comment['post_id']: comment['comments_count'] for comment in comments_count}

        posts_with_comments_count = list(self)
        for post in posts_with_comments_count:
            post.comments_count = count_for_id.get(post.id, 0)

        return posts_with_comments_count


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    objects = PostQuerySet.as_manager()


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    objects = TagQuerySet.as_manager()


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
