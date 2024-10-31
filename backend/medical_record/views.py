from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import MedicalRecord, PermissionRequest
from .serializers import (
    MedicalRecordSerializer, 
    MedicalRecordHistorySerializer, 
    PermissionRequestSerializer, 
    PermissionResponseSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import views, status
from django.utils import timezone
from userauth.models import User


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """
    GET: List the latest version of each medical record.
    POST: Create a new medical record for a specified user using the patient's email if the requester is a doctor and has permission.
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        # Ensure the requester is a doctor
        if not user.is_doctor:
            return Response({"message": "You don't have permission to create a medical record."}, status=status.HTTP_403_FORBIDDEN)
        
        # Get the patient's email from the request data
        patient_email = request.data.get("patient_email")
        if not patient_email:
            raise ValidationError({"patient_email": "This field is required to create a medical record for a specific patient."})

        # Verify that the patient exists
        try:
            patient = User.objects.get(email=patient_email)
        except User.DoesNotExist:
            raise NotFound(f"User with email {patient_email} not found.")

        # Check for an approved permission request for this doctor and patient
        permission_request = PermissionRequest.objects.filter(
            doctor=user,
            patient=patient,
            status="approved"
        ).first()

        if not permission_request:
            return Response(
                {"message": "You do not have permission from the patient to create a medical record."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Automatically set the doctor's name
        doctor_name = f"{user.first_name} {user.last_name}".strip()

        # Prepare the data for the medical record, including the doctor’s name
        medical_record_data = request.data.copy()
        medical_record_data["user"] = patient.id  # Link the medical record to the patient
        medical_record_data["doctor_name"] = doctor_name  # Automatically set the doctor's name

        # Serialize and save the medical record
        serializer = self.get_serializer(data=medical_record_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicalRecordRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve the latest version of a specific medical record.
    PUT: Update the medical record only if the doctor has permission from the patient.
    DELETE: Delete the medical record.
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        # Ensure the requester is a doctor
        if not user.is_doctor:
            return Response({"message": "You don't have permission to edit this record."}, status=status.HTTP_403_FORBIDDEN)

        # Get the specific medical record
        instance = self.get_object()

        # Check for an approved permission request for this doctor and record
        permission_request = PermissionRequest.objects.filter(
            doctor=user,
            patient=instance.user,
            medical_record=instance,
            status="approved"
        ).first()

        if not permission_request:
            return Response({"message": "You do not have permission from the patient to edit this medical record."}, status=status.HTTP_403_FORBIDDEN)

        # If permission exists, allow the update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user.is_doctor:
            return Response({"message": "You don't have permission to delete this record."}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

class MedicalRecordVersionsView(generics.ListAPIView):
    """
    GET: List all historical versions of a specific medical record.
    """
    serializer_class = MedicalRecordHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_doctor:
            raise PermissionDenied("You don't have permission to view medical record versions.")

        record_id = self.kwargs['pk']
        try:
            record = MedicalRecord.objects.get(pk=record_id)
            return record.history.all()
        except MedicalRecord.DoesNotExist:
            raise NotFound(f"MedicalRecord with id {record_id} not found.")


class MedicalRecordSpecificVersionView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific historical version of a medical record by history_id.
    """
    serializer_class = MedicalRecordHistorySerializer

    def get_object(self):
        user = self.request.user
        if not user.is_doctor:
            raise PermissionDenied("You don't have permission to view this version of the medical record.")

        record_id = self.kwargs['pk']
        history_id = self.kwargs['history_id']
        
        try:
            record = MedicalRecord.objects.get(pk=record_id)
            specific_version = record.history.get(history_id=history_id)
            return specific_version
        except (MedicalRecord.DoesNotExist, MedicalRecord.history.model.DoesNotExist):
            raise NotFound(f"Version with history_id {history_id} for MedicalRecord with id {record_id} not found.")
        
        
class RequestPermissionView(generics.CreateAPIView):
    """
    API View for doctors to request permission by providing medical_record_id in the request body.
    """
    serializer_class = PermissionRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        # Check if the requester is a doctor
        if not user.is_doctor:
            return Response(
                {"message": "Only doctors can request permission to access medical records."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Customize the response to include emails instead of IDs for clarity
        permission_request = PermissionRequest.objects.get(id=response.data['id'])
        response.data = {
            "id": permission_request.id,
            "doctor": permission_request.doctor.email,
            "patient": permission_request.patient.email,
            "medical_record": permission_request.medical_record.id,
            "status": permission_request.status,
            "request_date": permission_request.request_date,
            "response_date": permission_request.response_date
        }
        return response


class RespondToPermissionRequestView(generics.UpdateAPIView):
    """
    API View for patients to approve or deny access requests, with request_id in the body.
    """
    serializer_class = PermissionResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve `request_id` from the request body
        request_id = self.request.data.get("request_id")
        if not request_id:
            raise ValidationError({"request_id": "This field is required."})

        # Retrieve the specific permission request for the authenticated patient
        try:
            permission_request = PermissionRequest.objects.get(id=request_id, patient=self.request.user)
            return permission_request
        except PermissionRequest.DoesNotExist:
            raise NotFound("Permission request not found.")

    def perform_update(self, serializer):
        # Ensure that status is either 'approved' or 'denied'
        status = serializer.validated_data.get("status")
        if status not in ["approved", "denied"]:
            raise ValidationError({"status": "Status must be either 'approved' or 'denied'."})
        
        # Update status and response date
        serializer.save(response_date=timezone.now())

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Customize the response to use doctor and patient emails for clarity
        permission_request = self.get_object()
        response.data = {
            "id": permission_request.id,
            "doctor": permission_request.doctor.email,
            "patient": permission_request.patient.email,
            "medical_record": permission_request.medical_record.id,
            "status": permission_request.status,
            "request_date": permission_request.request_date,
            "response_date": permission_request.response_date
        }
        return response