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


Registration
============

If a new User want's an account he needs to register.
Registration is done with a POST request to the `/account/register/` endpoint.
Registration requires a captcha.

.. note::
  At the moment registration MUST only be done through WildFyre services.


Authentication
==============

-> See :doc:`auth`.


Confirming E-Mail
=================

When Users their E-Mail address, they get an email to their new address,
with a link to confirm their address.
Until this link is clicked the old address is used


Recovering Access
=================

When a user forgets his username or password he can recover his access.

.. note::
  At the moment account recovery MUST only be done through WildFyre services.


Recovering Usernames
--------------------

To get an email with all the usernames associated with a specific email address
make a `POST`-Request to the `/account/recover/` endpoint
with the email address, leaving the username field empty.
This requires a captcha.


Recovering Password
-------------------

If the user forgot his password he can request a that a token is sent to his
email, with a token to reset the password.

First make a `POST`-Request to the `/account/recover/` endpoint.
Fill out both email address and username. This action requires a captcha.
The returned data will contain a transaction id.

Then make a `POST`-Request to the `/account/recover/reset/` endpoint.
This requires the transaction id, as well as the token received by email.
Again a captcha is required.
