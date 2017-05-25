.. Heading is inset, to prevent 7 '=', which would trigger merge conflict linter

=========
 Banning
=========

Sometimes users behave band and have to be banned.

When the user takes an action, he is banned from doing,
he will get a `403: Forbidden`.


Own Bans
========

To check if the user is banned from at least one action make
a `GET`-request to the :doc:`profile <users>` of the user.

To list all active own bans make a `GET`-request to `/bans/`.

The list of bans should be checked, when the user is banned according to
his profile, or when an action fails unexpected with a 403


Ban Reasons
===========

The Ban reasons are the same as the reasons for :doc:`flagging <flag>`.


Auto Bans
=========

When our system identifies a users as harmful it might automatically ban him
(e.g. very much flags by high rep users or many flags marked as `spite`)

Auto bans are automatically removed when they are detected to be a mistake
(e.g. a moderator decides, that a post with many flags is ok)


Banned Users
============

Request the users :doc:`profile <users>` to check if he has at least one ban.

.. note::
    There is no way to find out from which actions another user is banned
