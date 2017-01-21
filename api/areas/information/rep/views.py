from rest_framework import generics
from areas.base.rep.views import ReputationView

from .serializers import ReputationSerializer
from .models import Reputation


class ReputationView(ReputationView):
    serializer_class = ReputationSerializer
    model = Reputation
