from rest_framework.viewsets import ModelViewSet

from application_form.api.serializers import ApplicationSerializer
from application_form.models import Application


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
