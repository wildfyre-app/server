========
Comments
========

Comments are displayed nested inside a post object.
So clients don't need to make a request for every comment.


Create Comment
==============

To create a comment simply make a `POST` request to the
:doc:`detail page <posts>` of the Post. In the request provide a `text`
attribute with the comment


Delete Comment
==============

To delete a comment make a `DELETE` request to
`/areas/<area>/<post_id>/<comment_id>`. The comment id is shown on the
post's detail page
