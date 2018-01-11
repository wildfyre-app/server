==========
Pagination
==========

Most of our list api endpoints use pagination.

Endpoints, that use pagination accept a `limit` and an `offset` query strings.
`limit` sets how much objects should be listed at max
and `offset` with which object to start the list (defaults to 0).

The api will provide a link to the previous and next set with the given `limit`
and the result set.
