from rest_framework.viewsets import ModelViewSet

from apartment.api.serializers import ApartmentSerializer
from apartment.models import Apartment


class ApartmentViewSet(ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
