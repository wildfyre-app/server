from rest_framework import generics, permissions

from .models import Ban
from .serializers import BanSerializer


class BanView(generics.ListAPIView):
    """
    List current active bans
    """
    queryset = Ban.active.all()
    serializer_class = BanSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
