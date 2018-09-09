from .registry import registry


def get_postid(post, nonce=None):
    if hasattr(post, 'pk') and hasattr(post, 'nonce'):
        return get_postid(post.pk, post.nonce)
    return "%s%s" % (nonce, post)
