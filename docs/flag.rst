========
Flagging
========

When a user sees inappropriate content they should be able to flag it.


Flag content
============

To Flag content make a `POST`-Request to the url with an appended '`flag/`'
with the required data.

.. note::
    Every user can only flag one content once. When trying to flag the same
    content again a 400 Status code is returned


Get Flag Reasons
================

The Flag Reasons are listed in the Response of an `OPTIONS` request,
and may change in the future.

.. note::
    Flag Reasons SHOULD NOT be hard coded.
    They Reasons MAY be cached for the current session.


Content that can be Flagged
===========================

Not everything can flagged.
Currently only the following can be flagged:

 * Post
 * Comment
