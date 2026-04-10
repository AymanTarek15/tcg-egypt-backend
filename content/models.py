from django.db import models
from django.conf import settings


class Article(models.Model):
    TYPE_CHOICES = [
        ("meta", "Meta Update"),
        ("tier_list", "Tier List"),
        ("news", "News"),
        ("guide", "Guide"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    article_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to="articles/", blank=True, null=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title