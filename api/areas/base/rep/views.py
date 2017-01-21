from rest_framework import generics, permissions


class ReputationView(generics.RetrieveAPIView):
    model = None
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Gets or creates the Reputation model for the user
        """
        assert self.model is not None, (
            "'%s' should either include a `model` attribute, "
            "or override the `get_object()` method."
            % self.__class__.__name__
            )

        obj, created = self.model.objects.get_or_create(user=self.request.user)

        self.check_object_permissions(self.request, obj)
        return obj
