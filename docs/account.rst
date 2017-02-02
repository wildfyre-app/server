============
User Account
============

This endpoint is used for actions on the user account itself.
Here the user can view and change his account data.

To view the data an :doc:`authenticated <auth>` GET request has to be made to
`/account/`::

    GET /account/ HTTP/1.1
    Host: api.wildfyre.net
    Authorization: token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

This will result in a JSON response simmilar the the one below.

.. code-block:: json

    {
        "id": 0,
        "username": "user",
        "email": "email@example.com"
    }

To change the email and/or the password do a `PATCH` request::

    PATCH /account/ HTTP/1.1
    Host: api.wildfyre.net
    Authorization: token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    Content-Type: application/json

    {
        "email": "newmail@example.com",
        "password": "secret"
    }

.. note::
    When changeing the email,
    an email is sent to the new address requesting the confirmation.


Authentication
==============

-> See :doc:`auth`.


Confirming E-Mail
=================

When Users their E-Mail address, they get an email to their new address,
with a link to confirm their address.
Until this link is clicked the old address is used
