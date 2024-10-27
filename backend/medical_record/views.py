from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import MedicalRecord
from .serializers import MedicalRecordSerializer, MedicalRecordHistorySerializer

class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """
    GET: List the latest version of each medical record.
    POST: Create a new medical record (initially version 1).
    """
    queryset = MedicalRecord.objects.all()  # No need for parent filtering with Simple History
    serializer_class = MedicalRecordSerializer


class MedicalRecordRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve the latest version of a specific medical record.
    PUT: Update the medical record (Django Simple History will track the changes).
    DELETE: Delete the medical record.
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    def update(self, request, *args, **kwargs):
        """
        Override update to save a new version automatically using Django Simple History.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()  # Simple History will log this as a new version
        return Response(serializer.data, status=status.HTTP_200_OK)


class MedicalRecordVersionsView(generics.ListAPIView):
    """
    GET: List all historical versions of a specific medical record.
    """
    serializer_class = MedicalRecordHistorySerializer

    def get_queryset(self):
        record_id = self.kwargs['pk']
        try:
            # Get the historical records for the specified MedicalRecord
            record = MedicalRecord.objects.get(pk=record_id)
            return record.history.all()  # Django Simple History's history manager
        except MedicalRecord.DoesNotExist:
            raise NotFound(f"MedicalRecord with id {record_id} not found.")


class MedicalRecordSpecificVersionView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific historical version of a medical record by history_id.
    """
    serializer_class = MedicalRecordHistorySerializer

    def get_object(self):
        record_id = self.kwargs['pk']
        history_id = self.kwargs['history_id']
        
        try:
            # Get the specific historical version by history_id
            record = MedicalRecord.objects.get(pk=record_id)
            specific_version = record.history.get(history_id=history_id)  # Get specific version by history_id
            return specific_version
        except (MedicalRecord.DoesNotExist, MedicalRecord.history.model.DoesNotExist):
            raise NotFound(f"Version with history_id {history_id} for MedicalRecord with id {record_id} not found.")
