from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Movie, Favorite, Rating


def normalize_text(text):
    text = text.lower().strip()

    translit = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sh",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }

    for rus, lat in translit.items():
        text = text.replace(rus, lat)

    return text


def home(request):
    if not request.user.is_authenticated:
        return redirect("register")

    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    all_movies = Movie.objects.all()

    if genre:
        all_movies = all_movies.filter(genre=genre)

    if query:
        search_text = normalize_text(query)
        filtered_movies = []

        for movie in all_movies:
            title = normalize_text(movie.title)
            description = normalize_text(movie.description)

            if search_text in title or search_text in description:
                filtered_movies.append(movie)

        movies = filtered_movies
    else:
        movies = all_movies

    favorite_ids = set(
        Favorite.objects.filter(
            user=request.user
        ).values_list("movie_id", flat=True)
    )

    return render(
        request,
        "movies/home.html",
        {
            "movies": movies,
            "query": query,
            "genre": genre,
            "favorite_ids": favorite_ids,
        },
    )


def movie_detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("register")

    movie = get_object_or_404(Movie, id=movie_id)

    is_favorite = Favorite.objects.filter(
        user=request.user,
        movie=movie
    ).exists()

    user_rating = Rating.objects.filter(
        user=request.user,
        movie=movie
    ).first()

    return render(
        request,
        "movies/movie_detail.html",
        {
            "movie": movie,
            "is_favorite": is_favorite,
            "user_rating": user_rating,
        },
    )


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(
                request,
                "movies/register.html",
                {
                    "error": "Заполните все поля"
                },
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "movies/register.html",
                {
                    "error": "Пользователь уже существует"
                },
            )

        user = User.objects.create_user(
            username=username,
            password=password,
        )

        login(request, user)

        return redirect("home")

    return render(
        request,
        "movies/register.html"
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            return redirect("home")

        return render(
            request,
            "movies/login.html",
            {
                "error": "Неверный логин или пароль"
            },
        )

    return render(
        request,
        "movies/login.html"
    )


def logout_view(request):
    logout(request)

    return redirect("home")


def toggle_favorite(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("register")

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        movie=movie,
    )

    if not created:
        favorite.delete()

    return redirect(
        "movie_detail",
        movie_id=movie.id
    )


def favorites(request):
    if not request.user.is_authenticated:
        return redirect("register")

    favorite_movies = Favorite.objects.filter(
        user=request.user
    ).select_related("movie")

    movies = [
        favorite.movie
        for favorite in favorite_movies
    ]

    return render(
        request,
        "movies/favorites.html",
        {
            "movies": movies,
        },
    )


def add_rating(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("register")

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    if request.method == "POST":
        value = int(
            request.POST.get(
                "value",
                0
            )
        )

        if 1 <= value <= 5:
            Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={
                    "value": value
                },
            )

    return redirect(
        "movie_detail",
        movie_id=movie.id
    )


def profile(request):
    if not request.user.is_authenticated:
        return redirect("register")

    favorite_count = Favorite.objects.filter(
        user=request.user
    ).count()

    user_ratings = Rating.objects.filter(
        user=request.user
    ).select_related("movie")

    rating_count = user_ratings.count()

    return render(
        request,
        "movies/profile.html",
        {
            "favorite_count": favorite_count,
            "rating_count": rating_count,
            "user_ratings": user_ratings,
        },
    )