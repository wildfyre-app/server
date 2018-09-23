=====
Areas
=====

Areas are where the magic happens.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    posts
    comments
    notifications
    rep

Available Areas
===============

To get all available areas make a `GET` request to `/areas/`.
A list of all available areas will be returned.

Each area has a name and a display name. The display name should be shown to the
user, while the name will be used internally (for example in the URL).

.. note::
    In the future there might be areas, that not every user can see.
