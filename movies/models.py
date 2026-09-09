from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=100, default="Drama")
    duration = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    poster = models.URLField(blank=True)

    video_url = models.URLField(
        blank=True, null=True, help_text="Разрешённая ссылка на видео"
    )

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="unique_user_movie_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.movie.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="user_ratings"
    )
    value = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="unique_user_movie_rating"
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.movie.title}: {self.value}"
