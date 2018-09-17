=====
Users
=====

The `/users/` endpoint provides the profile of the user itself or another user


Own Profile
===========

Make an :doc:`authenticated <auth>` GET request directly to `/users/`.
The authentication is required, because the system wouldn't know which user's
details to show.

You can edit this information trough a `PATCH` request with the data to change.
The only exception is `user`, which is read only.


Create
------

When a user doesn't have a profile, make a `POST` request to `/users/`,
with the required data.



Other Users Profile
===================

To view the profile of another user make a GET request to `/users/<id>`,
where `<id>` is the users unique id.
Which you can get from his posts or comments.

You can't edit the profile of another user.
Even when you access your own profile using the id, you can't edit it.



Fetch multiple profiles at once
-------------------------------

To get multiple profiles at once make a GET request to `/users/get/`
and specify each id of a target users as query parameter `id`.

e.g. `/users/get/?id=1&id=2&id=4`, will get the profiles of the user 1, 2 and 4.

.. note::
    If there is no user for a given id
    (because the user was recently deleted, etc) no error is raised, and the list
    will just not contain an entry for that user.
