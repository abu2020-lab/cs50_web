
from django.conf import settings
from django.urls import include, path


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost, name="newPost"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("like/<int:id>", views.like, name="like"),
    path("editpost/<int:id>", views.editpost, name="editpost")
]
