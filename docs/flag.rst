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

See :doc:`choices`.


Content that can be Flagged
===========================

Not everything can flagged.
Currently only the following can be flagged:

 * Post
 * Comment
