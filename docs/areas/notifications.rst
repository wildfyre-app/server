=============
Notifications
=============

A user will be automatically subscribed to all posts he created or commented on.

.. note::
    All requests on this page need to be :doc:`authenticated <../auth>`.

View Notifications
==================

To view notifications make an `GET` request to `/areas/notification/`.

A list will be returned with all unread comments with their post's area and id


Mark Notifications Read
=======================

Notifications are automatically marked read, when you view the respective post.


Subscribe to a post
===================

To subscribe to a post make a `POST` request to
`/areas/<area>/<post_id>/subscribe/`.

Set subscribe eighter to:

* true | 1 | t | y
* false | 0 | f | n

The value is case-insensitive.

.. note::
    When no value or an invalid value is specified for `subscribe`,
    `true` is assumed.
    This might change in the future

You're request should look simmilar to this::

    POST /areas/<area>/<id>/subscribe/ HTTP/1.1
    Host: api.wildfyre.net
    Authorization: token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    Content-Type: application/x-www-form-urlencoded

    subscribe=1
