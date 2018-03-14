import unittest
import django
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from .registry import registry
from .views import *
from .models import *
from bans.models import Ban
from flags.models import Flag, FlagComment


class AreasTest(APITestCase):
    def setUp(self):
        self.areas = registry.areas

    def test_areas(self):
        """
        Should return the areas

        When failing: Maybe implemented area, that can not be viewed by unauthenticated user
        """
        area_names = []
        for area in self.areas.values():
            area_names.append({'name': area.name})

        response = self.client.get(reverse('areas:areas'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, area_names)


@unittest.skipUnless(registry.areas, "No areas defined")
class QueueTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.author = get_user_model().objects.create_user(
            username='Author', password='secret')

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized
        """
        response = self.client.get(reverse('areas:queue', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_posts_empty(self):
        """
        Try to get posts (queue is empty)
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:queue', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts(self):
        """
        Get posts (queue has items)
        """
        self.client.force_authenticate(user=self.user)

        # Create posts
        posts = []
        posts.append(registry.get_area(self.area).Post().objects.create(author=self.author))
        posts.append(registry.get_area(self.area).Post().objects.create(author=self.author))
        posts.append(registry.get_area(self.area).Post().objects.create(author=self.author))

        init_stack = posts[0].stack_outstanding

        response = self.client.get(reverse('areas:queue', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check posts
        for p in posts:
            del p.stack_outstanding  # Refresh from db

            self.assertEqual(p.stack_outstanding, init_stack - 1)

            # Delete the post so it doesn't disturb any other test
            p.delete()

    def test_create_not_authenticated(self):
        """
        Unauthenticated users should not be able to Post
        """
        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_post(self):
        """
        Create a new post
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(registry.get_area(self.area).Post().objects.count(), 1)

        # Delete Create Object
        for p in registry.get_area(self.area).Post().objects.all():
            p.delete()


@unittest.skipUnless(registry.areas, "No areas defined")
class OwnTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        postModel = registry.get_area(self.area).Post()
        self.post = postModel.objects.create(author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Unauthenticated Users shouldn't be able to view this
        """
        response = self.client.get(reverse('areas:own', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own(self):
        """
        Try to get Posts, 1 post is available
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:own', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_own_none(self):
        """
        Try to get Posts, none available
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:own', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


@unittest.skipUnless(registry.areas, "No areas defined")
class DetailTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        postModel = registry.get_area(self.area).Post()
        self.post = postModel.objects.create(author=self.user_author, text="Hi there")
        self.anonym_post = postModel.objects.create(author=self.user_author, text="Hi there", anonym=True)

    def test_view_post(self):
        """
        Try to view a post
        """
        response = self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['anonym'])
        self.assertEqual(response.data['author']['user'], self.user_author.pk)
        
    def test_view_anonym_post(self):
        """
        Author should be displayed if the post is not anonym and author isn't deleted
        """
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.anonym_post.pk, 'nonce': self.anonym_post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['anonym'])
        self.assertIsNone(response.data['author'])

    def test_view_author_none(self):
        """
        Author might be None, because he got deleted
        """
        deleted_user = get_user_model().objects.create_user(
            username='DELETE ME', password='secret')

        postModel = registry.get_area(self.area).Post()
        post = postModel.objects.create(author=deleted_user, text="Hi there")

        deleted_user.delete();

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': post.pk, 'nonce': post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['author'])
        self.assertFalse(response.data['anonym'])

    def test_delete_post(self):
        """
        Try to delete own post
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.delete(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_others(self):
        """
        It should not be possible to delete other's post
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_not_authenticated(self):
        """
        Unauthenticated users should not be able to delete posts
        """
        response = self.client.delete(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@unittest.skipUnless(registry.areas, "No areas defined")
class CommentTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        postModel = registry.get_area(self.area).Post()
        self.post = postModel.objects.create(author=self.user_author, text="Hi there")

    def test_view_comment(self):
        """
        View a comment
        """
        comment = self.post.comment_set.create(author=self.user_author, text="Hi")

        response = self.client.get(
            reverse('areas:comment', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce, 'comment': comment.pk}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_not_authenticated(self):
        """
        Unauthenticated users shouldn't be able to comment
        """
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment(self):
        """
        Users may comment on other users posts
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.comment_set.count(), 1)

    def test_delete_comment(self):
        self.post.comment_set.create(author=self.user_author, text="Hi")
        self.assertEqual(self.post.comment_set.count(), 1)  # To check it worked

        self.client.force_authenticate(user=self.user_author)
        response = self.client.delete(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.post.comment_set.count(), 0)

    def test_delete_other_comment(self):
        self.post.comment_set.create(author=self.user_author, text="Hi")
        self.assertEqual(self.post.comment_set.count(), 1)  # To check it worked

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.post.comment_set.count(), 1)


@unittest.skipUnless(registry.areas, "No areas defined")
class SpreadTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        postModel = registry.get_area(self.area).Post()
        self.post = postModel.objects.create(author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Unauthenticated users should not be able to influence the spread
        """
        init_stack = self.post.stack_outstanding

        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'spread': True})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.post.stack_outstanding, init_stack)

    def test_spread_true(self):
        """
        Should increase stack_outstanding
        """
        self.post.stack_assigned.add(self.user)
        init_stack = self.post.stack_outstanding

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'spread': True})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(self.post.stack_outstanding, init_stack)

    def test_spread_false(self):
        """
        Should not change stack_outstanding
        """
        self.post.stack_assigned.add(self.user)
        init_stack = self.post.stack_outstanding

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'spread': False})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.stack_outstanding, init_stack)

    def test_not_queued(self):
        init_stack = self.post.stack_outstanding

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'spread': True})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.post.stack_outstanding, init_stack)


@unittest.skipUnless(registry.areas, "No areas defined")
class NotificationTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        postModel = registry.get_area(self.area).Post()
        self.post = postModel.objects.create(author=self.user_author, text="Hi there")

    def post_comment(self):
        comment_model = registry.get_area(self.area).comment_model
        # Ensure unique text (yes this is a do while)
        while True:
            text = "NotificationTest.post_comment_" + str(randint(0, 10**10))
            if not comment_model.objects.filter(text=text).exists():
                break

        self.client.force_authenticate(user=self.user)
        self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
            {'text': text})

        return comment_model.objects.get(author=self.user, text=text)

    def test_notification_not_authenticated(self):
        """
        Unauthenticated users don't have notifications (obviously)
        """
        response = self.client.get(reverse('areas:notification'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_notification_get_none(self):
        """
        If a user has no notifications, he shoudn't see any
        """
        self.user_author.comment_unread.clear()
        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:notification'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_notification_get(self):
        """
        A user should see their own notifications
        """
        # All comments are to the same post
        self.post_comment();
        self.post_comment();
        self.post_comment();

        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:notification') + "?limit=100")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['comments'], list(self.user_author.comment_unread.values_list('pk', flat=True)))

    def test_subscribe_not_authenticated(self):
        """
        Unautenticated users don't need to subscribe
        """
        response = self.client.post(reverse(
            'areas:subscribe',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe(self):
        """
        Subscribe to a post
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse(
            'areas:subscribe',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'subscribed': True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user in self.post.subscriber.all())

    def test_unsubscribe(self):
        """
        Unsubscribe from a post
        """
        self.post.subscriber.add(self.user)
        self.assertTrue(self.user in self.post.subscriber.all())  # Check

        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse(
            'areas:subscribe',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ), {'subscribed': False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user in self.post.subscriber.all())

    def test_auto_subscribe_post(self):
        """
        Auto subscribe, when posting the card
        """
        # As self.post has the autor self.user_author, he should be subscribed
        self.assertTrue(self.user_author in self.post.subscriber.all())

    def test_auto_subscribe_comment(self):
        """
        Auto subscribe, when posting a comment
        """
        self.post_comment()
        self.assertTrue(self.user in self.post.subscriber.all())

    def test_notifications(self):
        """
        Get Notifications
        """
        comment = self.post_comment()

        self.assertTrue(comment in self.user_author.comment_unread.all())

    def test_mark_read(self):
        """
        Mark Notifications read
        """
        comment = self.post_comment()

        self.client.force_authenticate(user=self.user_author)
        self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}
            ))

        self.assertFalse(comment in self.user_author.comment_unread.all())

    def test_mark_all_read(self):
        for _ in range(10):
            # Post 10 comments
            self.post_comment()

        self.client.force_authenticate(user=self.user_author)
        self.client.delete(reverse('areas:notification'))

        self.assertFalse(self.user_author.comment_unread.exists())

    def test_subscription_list(self):
        self.post.subscriber.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:subscribed', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.user.post_subscriber.count())


@unittest.skipUnless(registry.areas, "No areas defined")
class ReputationTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

    def test_not_authenticated(self):
        """
        Unauthenticated users don't have reputation and should get an Unauthorized error
        """
        response = self.client.get(reverse('areas:reputation', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_rep(self):
        """
        When a user has no rep, a new object should be created
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:reputation', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Reputation.objects.filter(area=self.area, user=self.user).exists())


@unittest.skipUnless(registry.areas, "No areas defined")
class FlagTest(APITestCase):
    def setUp(self):
        # Area to test with, use first area
        self.area = list(registry.areas)[0]
        # Test User
        self.author = get_user_model().objects.create_user(
            username='author', password='secret')
        self.reporter = get_user_model().objects.create_user(
            username='reporter', password='secret')

        # Test Post and Comment
        self.post = Post.objects.create(area=self.area, author=self.author)
        self.comment = self.post.comment_set.create(author=self.author)

    def test_not_authenticated(self):
        """
        Unauthenticated users may not falg content
        """
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_flag_post(self):
        """
        Flag a post
        """
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flag = Flag.objects.filter(object_id=self.post.pk)
        self.assertTrue(flag.exists())
        self.assertTrue(flag.get().comment_set.filter(reporter=self.reporter).exists())

    def test_flag_comment(self):
        """
        Flag a comment
        """
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce, 'comment': self.comment.pk}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flag = Flag.objects.filter(object_id=self.comment.pk)
        self.assertTrue(flag.exists())
        self.assertTrue(flag.get().comment_set.filter(reporter=self.reporter).exists())


class EnforceBanTest(APITestCase):
    def setUp(self):
        self.area = list(registry.areas)[0]

        self.user = get_user_model().objects.create_user(
            username='user', password='secret')
        Ban.objects.create(user=self.user, ban_all=True)

        goodguy = get_user_model().objects.create_user(
            username='goodguy', password='secret')
        self.post = registry.get_area(self.area).Post().objects.create(text="Sample Post", author=goodguy)

        # All requests should be authenticated as the banned user
        self.client.force_authenticate(user=self.user)

    def test_ban_post(self):
        """
        Test if banning of posting is enforced
        """
        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': 'Hello World'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ban_comment(self):
        """
        Test if banning of comments is enforced
        """
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ban_flag(self):
        """
        Test if banning of flaggin is enforced
        """
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'pk': self.post.pk, 'nonce': self.post.nonce}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
