=====
Posts
=====

Create Post
===========

To create a new Post, make a `POST` request to `/areas/<area>/posts/` and provid
the required data.


Getting Posts
=============

Every user has a stack of assigned posts. The application SHOULD preload them
if possible, and serve the user an already preloaded post.

To refill and retrive the users post make an :doc:`authenticated <../auth>`
`GET` request to `/areas/<area>/posts/`


Own Posts
==============

To list all the own posts, make a `GET` request to `/areas/<area>/posts/own/`


Delete
------

To delete on of the cards from a user make an :doc:`authenticated <../auth>`
`DELETE` request to `/areas/<area>/posts/<id>`.


View Post
=========

To view one Post in detail, no matter if the user has the card in his stack,
or isn't even authenticated, make a `GET` request to `/areas/<area>/posts/<id>`.


Spread
======

To remove a post from the users stack and spread or skip it make a
`POST` request to `/areas/<area>/posts/<id>/<spread>`,
where spread is eighter 1, to spread the post, or 2, to skip the post.

To spread or skip a post you need to have the card in your stack.
