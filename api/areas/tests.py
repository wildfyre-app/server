import unittest
import django
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from io import BytesIO
from PIL import Image

from django.contrib.auth import get_user_model

from . import get_postid
from .views import *
from .models import *
from bans.models import Ban
from flags.models import Flag, FlagComment


def create_areas():
    """
    Create multiple areas and return one of them
    """
    Area.objects.create(name='example2', displayname="2nd Example Area")
    Area.objects.create(name='somethingspecial', displayname="Something Special")
    Area.objects.create(name='dispnameunrelated', displayname="The cake is a lie.")

    return Area.objects.create(name='example', displayname="Example Area")


class AreasTest(APITestCase):
    def setUp(self):
        create_areas()
        self.areas = Area.objects.all()

    def test_areas(self):
        """
        Should return the areas

        When failing: Maybe implemented area, that can not be viewed by unauthenticated user
        """
        area_names = []
        for area in self.areas.values():
            area_names.append({'name': area['name'], 'displayname': area['displayname']})

        response = self.client.get(reverse('areas:areas'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, area_names)


class StatusTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

    def test_active_true(self):
        """
        Create a post. Expect the active flag to be true
        """
        p = Post.objects.create(area=self.area, author=self.user, text="Example")
        # Refresh from db to get annotation
        p = Post.all_objects.get(pk=p.pk)

        self.assertTrue(p.active)

    def test_active_old(self):
        """
        Create a post, set created to be older than one month. Expect the active flag to be false
        """
        p = Post.objects.create(area=self.area, author=self.user, text="Example")
        p.created = timezone.now() - datetime.timedelta(days=40)
        p.save()
        # Refresh from db
        p = Post.all_objects.get(pk=p.pk)

        self.assertFalse(p.active)


    def test_active_draft(self):
        """
        Create a draft/ Expect the active flag to be false.
        """
        p = Post.objects.create(area=self.area, author=self.user, draft=True)
        # Refresh form db
        p = Post.all_objects.get(pk=p.pk)


        self.assertFalse(p.active)


    def test_active_old_draft(self):
        """
        Create a draft. Set created to be older than one month. Expect the activ flag to be false.
        """
        p = Post.objects.create(area=self.area, author=self.user, draft=True)
        p.created = timezone.now() - datetime.timedelta(days=40)
        p.save()
        # Refresh from db
        p = Post.all_objects.get(pk=p.pk)

        self.assertFalse(p.active)


    def test_active_old_draft_published(self):
        """
        Create a draft. Set created to be older than one month. Publish it.
        Expect the active flag to be true.
        """
        p = Post.objects.create(area=self.area, author=self.user, draft=True, created=timezone.now() - datetime.timedelta(days=40))
        # Refresh from db
        # And ensure it's actually old enough
        p = Post.all_objects.get(pk=p.pk)
        self.assertFalse(p.active)
        p.publish()
        p.save()
        
        self.assertTrue(p.active)
        # And refresh again
        p = Post.all_objects.get(pk=p.pk)

        self.assertTrue(p.active)


class QueueTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
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
        posts.append(Post.objects.create(area=self.area, author=self.author))
        posts.append(Post.objects.create(area=self.area, author=self.author))
        posts.append(Post.objects.create(area=self.area, author=self.author))

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
        # Delete Create Object
        Post.objects.all().delete()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.filter(area=self.area).count(), 1)

    def test_create_with_image(self):
        """
        Create a new post, that contains a head image
        """
        # Delete Create Object
        Post.objects.all().delete()

        self.client.force_authenticate(user=self.user)

        # Image
        img = BytesIO()
        img.name = "test.png"
        Image.new('RGB', (1, 1)).save(img, "PNG")
        img.seek(0)

        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': "Hi", 'image': img})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.filter(area=self.area).count(), 1)


class OwnTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there")

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


class DraftTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there", draft=True)

    def test_not_authenticated(self):
        """
        Unauthenticated Users shouldn't be able to view this
        """
        response = self.client.get(reverse('areas:drafts', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own(self):
        """
        Try to get Posts, 1 post is available
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:drafts', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_own_none(self):
        """
        Try to get Posts, none available
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:drafts', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_draft_detail(self):
        """
        Try to get Draft Detail page of own draft
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:draft-detail', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_of_draft(self):
        """
        Try to get the normal detail page of a post that is in draft status.
        This should fail with a 404.
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.get(reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_modify_draft(self):
        """
        Drafts can still be modified
        """
        newText = "Modified this draft"
        self.client.force_authenticate(user=self.user_author)
        response = self.client.patch(
            reverse('areas:draft-detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': newText})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh object form db (can't just use del, because default manager doesn't find drafts)
        post = Post.all_objects.get(pk=self.post.pk)
        self.assertEqual(post.text, newText)
        self.assertTrue(post.draft)  # Must still be a draft

    def test_remove_image(self):
        """
        Try to remove an already attached image
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.patch(
            reverse('areas:draft-detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'image': None}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh object form db (can't just use del, because default manager doesn't find drafts)
        post = Post.all_objects.get(pk=self.post.pk)
        self.assertFalse(bool(post.image))
        self.assertTrue(post.draft)  # Must still be a draft

    def test_delete_draft(self):
        """
        Drafts should be deletable
        """
        self.client.force_authenticate(user=self.user_author)
        response = self.client.delete(reverse('areas:draft-detail', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.all_objects.filter(pk=self.post.pk).exists())

    def test_publish_draft(self):
        """
        Try to publish a draft
        """
        beforeRequest = timezone.now()

        self.client.force_authenticate(user=self.user_author)
        response = self.client.post(reverse('areas:draft-publish', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh object form db
        post = Post.objects.get(pk=self.post.pk)  # Should be available in objects manager now
        self.assertFalse(post.draft)
        self.assertGreater(post.created, beforeRequest)
        self.assertTrue(post.active)
        self.assertEqual(post.stack_outstanding, self.user_author.reputation_set.get(area=self.area).spread)


class AdditionalImagesTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        # Everything authenticated
        self.client.force_authenticate(user=self.user)

        # Post must be a draft
        self.post = Post.all_objects.create(area=self.area, author=self.user, text="Hi there", draft=True)

    def get_img_url(self, n):
        """
        Get the uri of the image n
        """
        return reverse('areas:draft-img', kwargs={'area': self.area, 'post': get_postid(self.post), 'img': n})

    def create_image(self):
        img = BytesIO()
        img.name = "test.png"
        Image.new('RGB', (1, 1)).save(img, "PNG")
        img.seek(0)
        return img

    def refresh_post(self):
        self.post = Post.all_objects.get(pk=self.post.pk)
        return self.post

    def test_add_img(self):
        """
        Add an image
        """
        response = self.client.put(self.get_img_url(0), {'image': self.create_image()})
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.post.additional_images.filter(num=0).exists())
        self.assertEqual(self.post.additional_images.get(num=0).comment, "")

    def test_remove_img(self):
        self.client.put(self.get_img_url(0), {'image': self.create_image()})

        response = self.client.delete(self.get_img_url(0))
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.post.additional_images.filter(num=0).exists())

    def test_remove_img_not_existing(self):
        # Make sure there are no images
        self.post.additional_images.all().delete()

        response = self.client.delete(self.get_img_url(0))
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.post.additional_images.filter(num=0).exists())

    def test_patch_comment(self):
        comment = "This is an image"

        self.client.put(self.get_img_url(0), {'image': self.create_image()})

        response = self.client.patch(self.get_img_url(0), {'comment': comment})
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.additional_images.get(num=0).comment, comment)

    def test_img_view_exist(self):
        self.client.put(self.get_img_url(0), {'image': self.create_image()})

        response = self.client.get(self.get_img_url(0))
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num'], 0)
        self.assertIsNotNone(response.data['image'])
        self.assertEqual(response.data['comment'], "")

    def test_img_view_not_exist(self):
        self.post.additional_images.all().delete()

        response = self.client.get(self.get_img_url(0))
        self.refresh_post()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.post.additional_images.filter(num=0).exists())
        self.assertEqual(response.data['num'], 0)
        self.assertIsNone(response.data['image'])
        self.assertEqual(response.data['comment'], "")

    def test_img_display(self):
        # Make sure only img with num=0 exists
        self.post.additional_images.all().delete()
        self.client.put(self.get_img_url(0), {'image': self.create_image()})

        response = self.client.get(reverse('areas:draft-detail', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        images = response.data['additional_images']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['num'], 0)
        self.assertIsNotNone(images[0]['image'])
        self.assertEqual(images[0]['comment'], "")

    def test_img_num_to_big(self):
        response = self.client.get(self.get_img_url(PostImage.MAX_NUM))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DetailTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there")
        self.anonym_post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there", anonym=True)

    def test_view_post(self):
        """
        Try to view a post
        """
        response = self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.anonym_post)}
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

        post = Post.objects.create(area=self.area, author=deleted_user, text="Hi there")

        deleted_user.delete();

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'post': get_postid(post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_others(self):
        """
        It should not be possible to delete other's post
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_not_authenticated(self):
        """
        Unauthenticated users should not be able to delete posts
        """
        response = self.client.delete(reverse(
            'areas:detail',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there")

    def test_view_comment(self):
        """
        View a comment
        """
        comment = self.post.comment_set.create(author=self.user_author, text="Hi")

        response = self.client.get(
            reverse('areas:comment', kwargs={'area': self.area, 'post': get_postid(self.post), 'comment': comment.pk}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_not_authenticated(self):
        """
        Unauthenticated users shouldn't be able to comment
        """
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment(self):
        """
        Users may comment on other users posts
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.comment_set.count(), 1)

    def test_create_comment_with_image(self):
        """
        A comment can be created with an optional image
        """
        self.client.force_authenticate(user=self.user)

        # Image
        img = BytesIO()
        img.name = "test.png"
        Image.new('RGB', (1, 1)).save(img, "PNG")
        img.seek(0)

        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': "Hi", 'image': img})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.comment_set.count(), 1)

    def test_delete_comment(self):
        comment = self.post.comment_set.create(author=self.user_author, text="Hi")
        self.assertEqual(self.post.comment_set.count(), 1)  # To check it worked

        self.client.force_authenticate(user=self.user_author)
        response = self.client.delete(
            reverse('areas:comment', kwargs={'area': self.area, 'post': get_postid(self.post), 'comment': comment.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.post.comment_set.count(), 0)

    def test_delete_comment_not_ownpost(self):
        comment = self.post.comment_set.create(author=self.user, text="Hi")
        self.assertEqual(self.post.comment_set.count(), 1)  # To check it worked

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('areas:comment', kwargs={'area': self.area, 'post': get_postid(self.post), 'comment': comment.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.post.comment_set.count(), 0)

    def test_delete_other_comment(self):
        self.post.comment_set.create(author=self.user_author, text="Hi")
        self.assertEqual(self.post.comment_set.count(), 1)  # To check it worked

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.post.comment_set.count(), 1)


class SpreadTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there")

    def test_not_authenticated(self):
        """
        Unauthenticated users should not be able to influence the spread
        """
        init_stack = self.post.stack_outstanding

        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ), {'spread': False})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.stack_outstanding, init_stack)

    def test_not_queued(self):
        init_stack = self.post.stack_outstanding

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse(
            'areas:spread',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ), {'spread': True})

        del self.post.stack_outstanding  # Force update
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.post.stack_outstanding, init_stack)


class NotificationTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
        # Test User
        self.user = get_user_model().objects.create_user(
            username='user', password='secret')

        self.user_author = get_user_model().objects.create_user(
            username='author', password='secret')

        # Test Posts
        self.post = Post.objects.create(area=self.area, author=self.user_author, text="Hi there")

    def post_comment(self):
        # Ensure unique text (yes this is a do while)
        while True:
            text = "NotificationTest.post_comment_" + str(randint(0, 10**10))
            if not Comment.objects.filter(text=text).exists():
                break

        self.client.force_authenticate(user=self.user)
        self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': text})

        return Comment.objects.get(author=self.user, text=text)

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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe(self):
        """
        Subscribe to a post
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse(
            'areas:subscribe',
            kwargs={'area': self.area, 'post': get_postid(self.post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
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
            kwargs={'area': self.area, 'post': get_postid(self.post)}
            ))

        self.assertFalse(comment in self.user_author.comment_unread.all())

    def test_mark_all_read(self):
        for _ in range(10):
            # Post 10 comments
            self.post_comment()

        self.client.force_authenticate(user=self.user_author)
        response = self.client.delete(reverse('areas:notification'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user_author.comment_unread.exists())

    def test_subscription_list(self):
        self.post.subscriber.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('areas:subscribed', kwargs={'area': self.area}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.user.post_subscriber.count())


class ReputationTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
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


class FlagTest(APITestCase):
    def setUp(self):
        self.area = create_areas()
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
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'post': get_postid(self.post)}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_flag_post(self):
        """
        Flag a post
        """
        self.client.force_authenticate(user=self.reporter)
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'post': get_postid(self.post)}),
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
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'post': get_postid(self.post), 'comment': self.comment.pk}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flag = Flag.objects.filter(object_id=self.comment.pk)
        self.assertTrue(flag.exists())
        self.assertTrue(flag.get().comment_set.filter(reporter=self.reporter).exists())


class EnforceBanTest(APITestCase):
    def setUp(self):
        self.area = create_areas()

        self.user = get_user_model().objects.create_user(
            username='user', password='secret')
        Ban.objects.create(user=self.user, ban_all=True)

        goodguy = get_user_model().objects.create_user(
            username='goodguy', password='secret')

        self.post = Post.objects.create(area=self.area, text="Sample Post", author=goodguy)

        # All requests should be authenticated as the banned user
        self.client.force_authenticate(user=self.user)

    def test_ban_post(self):
        """
        Test if banning of posting is enforced
        """
        response = self.client.post(reverse('areas:queue', kwargs={'area': self.area}), {'text': 'Hello World'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ban_publish_draft(self):
        """
        Test if banning of posting is enforced for drafts
        """
        post = Post.all_objects.create(area=self.area, text="Sample Draft", author=self.user, draft=True)
        
        response = self.client.post(reverse('areas:draft-publish', kwargs={'area': self.area, 'post': get_postid(post)}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post = Post.all_objects.get(pk=post.pk)
        self.assertTrue(post.draft)

    def test_ban_allow_draft(self):
        """
        Banning should not prevent the creation of Drafts
        """
        response = self.client.post(reverse('areas:drafts', kwargs={'area': self.area}), {'text': 'Hello World'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.all_objects.get(area=self.area, author=self.user)
        self.assertTrue(post.draft)  # Must be a draft

    def test_ban_comment(self):
        """
        Test if banning of comments is enforced
        """
        response = self.client.post(
            reverse('areas:detail', kwargs={'area': self.area, 'post': get_postid(self.post)}),
            {'text': "Hi"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ban_flag(self):
        """
        Test if banning of flaggin is enforced
        """
        response = self.client.post(reverse('areas:flag', kwargs={'area': self.area, 'post': get_postid(self.post)}),
                                    {'reason': Flag.Reason.SPAM.value})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
