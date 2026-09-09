from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path(
        "movie/<int:movie_id>/favorite/", views.toggle_favorite, name="toggle_favorite"
    ),
    path("movie/<int:movie_id>/rating/", views.add_rating, name="add_rating"),
    path("favorites/", views.favorites, name="favorites"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
]
