from rest_framework import generics

from . import BAN_REASON_CHOICES, FLAG_REASON_CHOICES
from .serializers import ReasonSerializer


class BanReasonView(generics.ListAPIView):
    serializer_class = ReasonSerializer
    queryset = BAN_REASON_CHOICES


class FlagReasonView(generics.ListAPIView):
    serializer_class = ReasonSerializer
    queryset = FLAG_REASON_CHOICES
