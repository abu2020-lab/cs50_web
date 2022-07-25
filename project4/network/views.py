from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import OuterRef, Count
from django.core.paginator import Paginator


from .models import User, Post, Follower, Like

MAX_POSTS_PER_PAGE = 10

class NewPostForm(forms.Form):
    post_text = forms.Field(widget=forms.Textarea({'rows': '3','maxlength' : 160,'class': 'form-control', 'placeholder': "What's Happening?", 'id': 'id_post_edit_text'
        }),
        label="New Post", required=True)

class NewEditPostForm(forms.Form):
    id_post_edit_text = forms.Field(widget=forms.Textarea({
        'rows': '3',
        'maxlength': 160,
        'class': 'form-control',
        'placeholder': "What's happening?",
        'id': 'id_post_edit_text'
    }),
    label="New Post", required=True)





def index(request):
    if request.user.is_authenticated:
        user = request.session['_auth_user_id']
        likes = Like.objects.filter(post=OuterRef('id'), user_id=user)
        posts = Post.objects.filter().order_by('-post_date').annotate(current_like=Count(likes.values('id')))
    else:
        posts = Post.objects.order_by('-post_date').all()

    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html" , {
        'posts': page_obj,
        'form': NewPostForm(),
        'form_edit': NewEditPostForm()        
    })

def following(request):
    if request.user.is_authenticated:
        user = request.session['_auth_user_id']
        followers = Follower.objects.filter(follower=user)
        likes = Like.objects.filter(post=OuterRef('id'), user_id=user)
        posts = Post.objects.filter(user_id___in=followers.values('following_id')).order_by('-post_date').annotate(current_like=Count(likes.values('id')))
    else:
        return HttpResponseRedirect(reverse("login"))

    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        'posts': page_obj,
        'form': NewPostForm()
    })


def profile(request, username):
    is_following = 0
    profile_user = User.objects.get(username=username)
    if request.user.is_authenticated:
        logged_user = request.session['_auth_user_id']
        is_following = Follower.objects.filter(follower=logged_user, following=profile_user).count()
        likes = Like.objects.filter(post=OuterRef('id'), user_id=logged_user)
        posts = Post.objects.filter(user=profile_user).order_by('post_date').annotate(current_like=Count(likes.values('id')))
    else:
        posts = Post.objects.filter(user=profile_user).order_by('post_date').all()

    total_following = Follower.objects.filter(follower=profile_user).count()
    total_followers = Follower.objects.filter(following=profile_user).count()

    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "user_profile": profile_user,
        "posts": page_obj,
        "is_following": is_following,
        'total_following': total_following,
        'total_followers': total_followers,
        'form': NewPostForm(),
        'form_edit': NewEditPostForm()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def newpost(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.session['_auth_user_id'])
            text = form.cleaned_data["post_text"]
            post = Post(user=user, text=text)
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(reverse("index"))
