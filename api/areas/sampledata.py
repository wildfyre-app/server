from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

from sampledata import register

from django.contrib.auth import get_user_model

from .registry import registry


Post = registry.get_area(list(registry.areas)[0]).Post()
admin = get_user_model().objects.get(pk=1)
user = get_user_model().objects.get(pk=2)


def create_image():
    buffer = BytesIO()
    Image.new('RGB', (100, 100), (255, 0, 0)).save(buffer, "PNG")
    image = ContentFile(buffer.getvalue())
    return InMemoryUploadedFile(image, None, "test.png", 'image/png', image.tell, None)


@register()
def selfPost():
    post = Post.objects.create(author=admin, text="Post by admin\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit.")
    post.comment_set.create(author=admin, text="First comment, by admin.\n\nPhasellus fringilla odio vitae nibh aliquet facilisis.", )
    post.comment_set.create(author=user, text="Another comment.\n\nNunc pellentesque urna eget ipsum vestibulum luctus. Praesent fermentum purus at pellentesque molestie.")


@register()
def otherPost():
    post = Post.objects.create(author=user, text="Duis blandit sagittis leo. Vestibulum et sodales ante. Curabitur et pulvinar sem. Integer lacinia pharetra ante quis varius. Name egestas blandit faucibus. Ut id velit risus.")
    post.comment_set.create(author=admin, text="Wow cool. You should write books. I really like your words.")
    c = post.comment_set.create(author=user, text="Thank you. Really appreciate it.")
    c.image.save("test.png", create_image())


@register()
def selfAnonPost():
    post = Post.objects.create(author=admin, text="Example anon post by admin user.", anonym=True)
    post.comment_set.create(author=admin, text="Hey, who are you to claim that you are me.")
    post.comment_set.create(author=user, text="It would be funny, if it were actually you.")
    post.image.save("test.png", create_image())


@register()
def otherAnonPost():
    post = Post.objects.create(author=user, text="↑↑↓↓←→←→ba", anonym=True)
    post.comment_set.create(author=admin, text="コナミコマンド")
    post.comment_set.create(author=user, text="If some chars on this page don't display correctly, you probably need a different font❗")


@register()
def selfDraft():
    post = Post.objects.create(author=admin, text="Example draft", draft=True)
