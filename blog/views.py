from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author_name,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.related_tags],
        'first_tag_title': post.related_tags[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    popular_tags = Tag.objects.popular()
    all_posts = Post.objects.prefetch_with_related_tags()
    most_popular_posts = all_posts.popular().prefetch_related(Prefetch('author', to_attr='author_name'))[:5] \
        .fetch_with_comments_count()
    fresh_posts = all_posts.order_by('published_at').prefetch_related(Prefetch('author', to_attr='author_name')) \
        .fetch_with_comments_count()
    most_fresh_posts = list(fresh_posts)[:5]
    most_popular_tags = popular_tags[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    popular_tags = Tag.objects.popular()
    all_posts = Post.objects.prefetch_with_related_tags()
    most_popular_posts = all_posts.popular().prefetch_related(Prefetch('author', to_attr='author_name'))[:5] \
        .fetch_with_comments_count()
    most_popular_tags = popular_tags[:5]
    posts = all_posts.popular().prefetch_related(Prefetch('author', to_attr='author_name')).fetch_with_comments_count()
    comments = Comment.objects.prefetch_related(Prefetch('author', to_attr='author_name'))

    idx = 0
    for post in posts:
        if post.slug == slug:
            break
        else:
            idx += 1

    post = posts[idx]

    comments = comments.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author_name,
        })

    likes = post.likes.all()

    related_tags = post.related_tags

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author_name,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    popular_tags = Tag.objects.popular()
    all_posts = Post.objects.prefetch_with_related_tags()
    most_popular_posts = all_posts.popular().prefetch_related(Prefetch('author', to_attr='author_name'))[:5] \
        .fetch_with_comments_count()
    most_popular_tags = popular_tags[:5]

    tag = get_object_or_404(popular_tags, title=tag_title)

    related_posts = tag.posts.all()[:20].prefetch_with_related_tags().prefetch_related(Prefetch
                                                                                     ('author',
                                                                                      to_attr='author_name'))\
        .fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
