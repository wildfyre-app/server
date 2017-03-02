import django
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import *
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class PostTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('areas:information:posts:post'))
        request.user = AnonymousUser()
        response = PostView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_get_posts(self):
        """
        Trying to get posts
        """
        request = self.factory.get(reverse('areas:information:posts:post'))
        force_authenticate(request, self.user)
        response = PostView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        """
        Create a new post
        """
        request = self.factory.post(reverse('areas:information:posts:post'), {'text': "Hi"})
        force_authenticate(request, self.user)
        response = PostView.as_view()(request)

        self.assertEqual(response.status_code, 201)

class DetailTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(author=self.user_author, text="Hi there")
        self.post_own = Post.objects.create(author=self.user, text="Hi there")

    def test_view_post(self):
        """
        Try to view a post
        """
        request = self.factory.get(reverse('areas:information:posts:detail', kwargs={'pk': self.post.pk, 'nonce': self.post.nonce}))
        response = DetailView.as_view()(request, pk=self.post.pk, nonce=self.post.nonce)

        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        """
        Try to delete post
        """
        request = self.factory.delete(reverse('areas:information:posts:detail', kwargs={'pk': self.post_own.pk, 'nonce': self.post_own.nonce}))
        force_authenticate(request, self.user)
        response = DetailView.as_view()(request, pk=self.post_own.pk, nonce=self.post_own.nonce)

        self.assertEqual(response.status_code, 204)

    def test_delete_others(self):
        """
        Users must not be able to delete a post of someone else
        """
        request = self.factory.delete(reverse('areas:information:posts:detail', kwargs={'pk': self.post.pk, 'nonce': self.post.nonce}))
        force_authenticate(request, self.user)
        response = DetailView.as_view()(request, pk=self.post.pk, nonce=self.post.nonce)

        self.assertEqual(response.status_code, 403)

    def test_delete_as_anon(self):
        """
        AnonymousUser must not be able to delete a post of someone else
        """
        request = self.factory.delete(reverse('areas:information:posts:detail', kwargs={'pk': self.post.pk, 'nonce': self.post.nonce}))
        request.user = AnonymousUser()
        response = DetailView.as_view()(request, pk=self.post.pk, nonce=self.post.nonce)

        self.assertEqual(response.status_code, 401)

class OwnTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('areas:information:posts:own'))
        request.user = AnonymousUser()
        response = PostView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_get_own(self):
        """
        Try to get the own posts
        """
        request = self.factory.get(reverse('areas:information:posts:own'))
        force_authenticate(request, self.user_author)
        response = OwnView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_get_no_posts(self):
        """
        Try to get the own posts, when not having any
        """
        request = self.factory.get(reverse('areas:information:posts:own'))
        force_authenticate(request, self.user)
        response = OwnView.as_view()(request)

        self.assertEqual(response.status_code, 200)

class SpreadTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(author=self.user_author, text="Hi there")

    def test_spread_true(self):
        """
        Should respond with 204: No Content
        and increasse the stack count with the user spread
        """
        self.post.stack_assigned.add(self.user)
        old_stack = self.post.stack_count

        request = self.factory.post(reverse('areas:information:posts:spread', kwargs={
            'pk': self.post.id,
            'nonce': self.post.nonce,
            'spread': 1
            }))
        force_authenticate(request, self.user)
        response = SpreadView.as_view()(request, pk=self.post.id, nonce=self.post.nonce, spread=1)


        user_spread = Reputation.objects.get(user=self.user).spread
        new_stack = Post.objects.get(pk=self.post.pk).stack_count

        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_stack, old_stack + user_spread)

    def test_spread_false(self):
        """
        Should respond with 204: No Content
        And don't increasethe stack count
        """
        self.post.stack_assigned.add(self.user)
        old_stack = self.post.stack_count

        request = self.factory.post(reverse('areas:information:posts:spread', kwargs={
            'pk': self.post.id,
            'nonce': self.post.nonce,
            'spread': 0
            }))
        force_authenticate(request, self.user)
        response = SpreadView.as_view()(request, pk=self.post.id, nonce=self.post.nonce, spread=0)


        new_stack = Post.objects.get(pk=self.post.pk).stack_count

        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_stack, old_stack)


class CommentTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.post(reverse('areas:information:posts:detail', kwargs={'pk': self.post.pk, 'nonce': self.post.nonce}),
                                   {'text': "hi"})
        request.user = AnonymousUser()
        response = PostView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_comment(self):
        """
        Comment should be created
        Also status code 201: Created should be raised
        """
        request = self.factory.post(reverse('areas:information:posts:detail', kwargs={'pk': self.post.pk, 'nonce': self.post.nonce}),
                                   {'text': "hi"})
        force_authenticate(request, self.user)
        response = DetailView.as_view()(request, pk=self.post.id, nonce=self.post.nonce)

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.post.comment_set.count(), 1)