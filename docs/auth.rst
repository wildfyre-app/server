==============
Authentication
==============

.. note::
    You SHOULD authenticate every request, when a user is logged in.

We use token based authentication. To authenticate a user add an `Authorization`
header with the value `token <token>` where `<token>` is the users token

.. code-block:: http
    :emphasize-lines: 3

    GET /account/ HTTP/1.1
    Host: api.wildfyre.net
    Authorization: token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

For Security Reasons the Username and Password SHOULD NOT be saved.
Instead save the token.


Retrive the Token
=================

To retrive the token of a user, make a `POST` request to `/account/auth/`
with the username and password::

    POST /account/auth/ HTTP/1.1
    Host: api.wildfyre.net
    Content-Type: application/json

    {
        "username": "user",
        "password": "secret"
    }

The reponse will be a JSON object with the Token.
