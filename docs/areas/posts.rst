=====
Posts
=====

Create Post
===========

To create a new Post, make a `POST` request to `/areas/<area>/` and provide
the required data.


Anonym Posts
------------

To make an anonym post, set `anonym` to `true`.
On an anonym post `author` is always `null`, but `author` can also be `null` when the post wasn't anonym.


Drafts
======

Drafts can not be viewed by other users, are assigned an id, that they will
keep even after they are published. Drafts are not shown as Own Posts.

Create a draft
--------------

Drafts can be created by sending a `POST`-ing them to `/areas/<area>/drafts`.


Editing and deleting a draft
----------------------------

Drafts can be deleted with `DELETE` and edited with `PUT` and `PATCH` requests
at the `/areas/<area>/drafts/<id>` endpoint.


Listing drafts
--------------

All current drafts of a user can be viewed with
a `GET` request to `/areas/<area>/drafts/`.


Publishing drafts
-----------------

Publishing a draft converts it to a normal post, therefore removes it from
the list of drafts, adds it to the list of own posts and makes it available
in the queue of other users.

To publish a draft make an empty
`POST` request to `/areas/<area>/drafts/<id>/publish/`.

Posts cannot be converted back into the draft stage.


Getting Posts
=============

Every user has a stack of assigned posts. The application SHOULD preload them
if possible, and serve the user an already preloaded post.

To refill and retrieve the users post make an :doc:`authenticated <../auth>`
`GET` request to `/areas/<area>/`


Own Posts
=========

To list all the own posts, make a `GET` request to `/areas/<area>/own/`


Delete
------

To delete on of the cards from a user make an :doc:`authenticated <../auth>`
`DELETE` request to `/areas/<area>/<id>`.


View Post
=========

To view one Post in detail, no matter if the user has the card in his stack,
or isn't even authenticated, make a `GET` request to `/areas/<area>/<id>`.


Spread
======

To remove a post from the users stack and spread or skip it make a
`POST` request to `/areas/<area>/<id>/spread/`.
Set the `spread` attribute to true to spread the post and to false to skip it.

To spread or skip a post you need to have the card in your stack.
