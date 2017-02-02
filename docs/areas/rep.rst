==========
Reputation
==========

A users reputation decides the spread amount of the user.

To get a users reputation make a `GET` request to `/areas/<area>/rep/`.
The response is a JSON object, with the reputation, and the resulting spread.

The repuation gain/loss for a given action is always the same.
But the heigher the spread is, the more additional reputation is needed, to
get to the next spread level.

.. note::
    A User can only get his own reputation and spread.
