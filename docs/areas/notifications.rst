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

To mark all notifications as read make a `DELETE` request
to `/areas/notification/`.


Subscribe to a post
===================

To update your subscription status of a post make a `PUT` request to
`/areas/<area>/<post_id>/subscribe/`.
