from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.utils import timezone
from collections import defaultdict
from .models import MedicalRecord, PermissionRequest
from userauth.models import User, Doctor, Patient
from django.db import transaction
from .serializers import (
    MedicalRecordSerializer,
    MedicalRecordHistorySerializer,
    PermissionRequestSerializer,
    PermissionResponseSerializer,
)


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """
    GET: List all medical records for a specific patient.
    POST: Create a new version of a medical record if an update is needed.
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user  # Should be a User instance

        # Ensure the requester is a doctor
        try:
            doctor = user.doctor_profile  # Access the Doctor instance
        except Doctor.DoesNotExist:
            return Response(
                {"message": "You don't have permission to create a medical record."},
                status=status.HTTP_403_FORBIDDEN
            )

        patient_email = request.data.get("patient_email")
        if not patient_email:
            raise ValidationError({"patient_email": "This field is required to create a medical record."})

        # Verify the patient exists
        try:
            patient = Patient.objects.get(user__email=patient_email)
        except Patient.DoesNotExist:
            raise NotFound(f"Patient with email {patient_email} not found.")

        # Check for an existing active record
        existing_record = MedicalRecord.objects.filter(user=patient.user).first()

        if existing_record:
            return Response(
                {
                    "message": "A medical record for this patient already exists.",
                    "medical_record_id": existing_record.id,
                    "details": existing_record.id,
                },
                status=status.HTTP_200_OK,
            )

        # Create a new medical record
        hospital_name = doctor.hospital.name
        hospital_address = doctor.hospital.address
        doctor_name = f"{user.first_name} {user.last_name}".strip()

        medical_record = MedicalRecord.objects.create(
            user=patient.user,
            date=timezone.now(),
            doctor_name=doctor_name,
            hospital_name=hospital_name,
            hospital_address=hospital_address,
        )

        return Response(
            {"message": "Medical record created successfully.", "medical_record_id": medical_record.id},
            status=status.HTTP_201_CREATED,
        )
        
    def list(self, request, *args, **kwargs):
        """
        Group medical records by user email and return as a structured response.
        """
        # Query all medical records and prefetch related user data
        queryset = self.get_queryset().select_related('user')

        # Group records by user email
        grouped_records = defaultdict(list)
        for record in queryset:
            grouped_records[record.user.email].append(record)

        # Serialize the grouped data
        response_data = {
            user_email: MedicalRecordSerializer(records, many=True).data
            for user_email, records in grouped_records.items()
        }

        return Response(response_data, status=status.HTTP_200_OK)
        
    
class MedicalRecordRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET: Retrieve a specific medical record.
    PUT: Allow updates only by the doctor who has been granted edit permission.
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user  # Should be a User instance
        instance = self.get_object()

        # Ensure the requester is a doctor
        try:
            doctor = user.doctor_profile
        except Doctor.DoesNotExist:
            return Response(
                {"message": "You don't have permission to update this medical record."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the doctor has permission to edit this medical record
        try:
            permission_request = PermissionRequest.objects.get(
                medical_record=instance,
                doctor=user,  # 'doctor' field in PermissionRequest is a ForeignKey to User
                status="approved",
                edit_permission=True,
            )
        except PermissionRequest.DoesNotExist:
            return Response(
                {"message": "You do not have permission to edit this medical record."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prepare data for comparison
        data = request.data.copy()
        excluded_fields = ['id', 'user', 'date', 'previous_version', 'doctor_name']
        changes_detected = False
        changed_fields = []

        # Get all field names from the model, excluding read-only fields
        model_fields = [field.name for field in instance._meta.fields if field.name not in excluded_fields]

        # Compare each field to see if changes were made
        for field in model_fields:
            new_value = data.get(field, getattr(instance, field))
            old_value = getattr(instance, field)

            # Normalize None and string values for comparison
            if str(new_value).strip() != str(old_value).strip():
                changes_detected = True
                changed_fields.append(field)

        # If no changes, return a response indicating that
        if not changes_detected:
            return Response(
                {"message": "No changes were made to the medical record."},
                status=status.HTTP_200_OK,
            )

        # Create a new instance with updated data
        new_data = {field: getattr(instance, field) for field in model_fields}  # Copy existing data
        new_data.update(data)  # Apply updates
        new_data['user'] = instance.user.id  # Assign the primary key of the User instance
        new_data['doctor_name'] = f"{user.first_name} {user.last_name}".strip()
        new_data['date'] = timezone.now()

        # Create the new record
        serializer = self.get_serializer(data=new_data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()

        return Response(
            {
                "message": "Medical record updated successfully. A new version has been created.",
                "changed_fields": changed_fields,
                "medical_record_id": new_instance.id,
            },
            status=status.HTTP_201_CREATED,
        )
class MedicalRecordVersionsView(generics.ListAPIView):
    """
    GET: List all historical versions of a specific medical record.
    """
    serializer_class = MedicalRecordHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Ensure the requester is a doctor
        if not hasattr(user, 'doctor_profile'):
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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        # Ensure the requester is a doctor
        if not hasattr(user, 'doctor_profile'):
            raise PermissionDenied("You don't have permission to view this version of the medical record.")

        record_id = self.kwargs['pk']
        history_id = self.kwargs['history_id']

        try:
            record = MedicalRecord.objects.get(pk=record_id)
            return record.history.get(history_id=history_id)
        except (MedicalRecord.DoesNotExist, MedicalRecord.history.model.DoesNotExist):
            raise NotFound(f"Version with history_id {history_id} for MedicalRecord with id {record_id} not found.")

class RequestPermissionView(generics.CreateAPIView):
    """
    API View for doctors to request permission from patients to modify a specific medical record.
    """
    serializer_class = PermissionRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        # Ensure the requester is a doctor
        if not hasattr(user, 'doctor_profile'):
            return Response(
                {"message": "Only doctors can request permission to modify medical records."},
                status=status.HTTP_403_FORBIDDEN,
            )

        doctor = user  # User instance representing the doctor
        patient_email = request.data.get("patient_email")
        medical_record_id = request.data.get("medical_record_id")

        # Validate input data
        if not patient_email or not medical_record_id:
            return Response(
                {
                    "errors": {
                        "patient_email": "This field is required." if not patient_email else None,
                        "medical_record_id": "This field is required." if not medical_record_id else None,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify that the patient exists
        try:
            patient = Patient.objects.get(user__email=patient_email)
        except Patient.DoesNotExist:
            raise NotFound(f"Patient with email '{patient_email}' not found.")

        # Verify that the medical record exists and belongs to the patient
        try:
            medical_record = MedicalRecord.objects.get(id=medical_record_id, user=patient.user)
        except MedicalRecord.DoesNotExist:
            raise NotFound(f"Medical record with ID '{medical_record_id}' not found for this patient.")

        # Check if there is already a pending request for the same medical record by the same doctor
        existing_pending_request = PermissionRequest.objects.filter(
            doctor=doctor,
            medical_record=medical_record,
            status="pending"
        ).first()

        if existing_pending_request:
            return Response(
                {
                    "message": "You already have a pending request for this medical record.",
                    "details": {
                        "id": existing_pending_request.id,
                        "status": existing_pending_request.status,
                        "response_date": existing_pending_request.response_date,
                    },
                },
                status=status.HTTP_200_OK,
            )

        # Create the permission request
        permission_request = PermissionRequest.objects.create(
            doctor=doctor,
            patient=patient.user,
            medical_record=medical_record,
            status="pending",
            request_date=timezone.now(),
        )

        # Serialize and return the created permission request
        serializer = self.get_serializer(permission_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class RespondToPermissionRequestView(APIView):
    """
    API View for patients to approve or deny access requests for a specific doctor.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic  # Ensures atomicity of the operation
    def put(self, request, *args, **kwargs):
        permission_request_id = request.data.get("permission_request_id")
        status_value = request.data.get("status")

        # Validate input data
        errors = {}
        if not permission_request_id:
            errors["permission_request_id"] = "This field is required."
        if not status_value:
            errors["status"] = "This field is required."
        elif status_value not in ["approved", "denied"]:
            errors["status"] = "Status must be either 'approved' or 'denied'."
        if errors:
            raise ValidationError(errors)

        user = request.user

        # Ensure the requester is a patient
        if not hasattr(user, 'patient_profile'):
            raise PermissionDenied("You don't have permission to respond to permission requests.")

        # Retrieve the specific permission request
        try:
            permission_request = PermissionRequest.objects.select_related('doctor', 'medical_record').get(
                id=permission_request_id,
                patient=user  # Ensure the patient matches the current user
            )
        except PermissionRequest.DoesNotExist:
            raise NotFound("Permission request not found.")
        except PermissionRequest.MultipleObjectsReturned:
            raise ValidationError("Multiple permission requests found with the same ID. Please contact support.")

        # Update the status and edit_permission
        permission_request.status = status_value
        permission_request.response_date = timezone.now()
        permission_request.edit_permission = (status_value == "approved")
        permission_request.save()

        # Serialize and return the updated permission request
        response_data = {
            "id": permission_request.id,
            "doctor": permission_request.doctor.email,
            "status": permission_request.status,
            "medical_record_id": permission_request.medical_record.id,
            "edit_permission": permission_request.edit_permission,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    
class DeletePermissionRequestsToPatientView(APIView):
    """
    API View to delete all permission requests made to a specific patient.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Ensure the user is a patient
        if not hasattr(request.user, 'patient_profile'):
            return Response(
                {"message": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all permission requests associated with the patient
        deleted_count, _ = PermissionRequest.objects.filter(patient=request.user).delete()

        # Respond with the number of deleted permission requests
        return Response(
            {"message": f"Deleted {deleted_count} permission request(s) made to you."},
            status=status.HTTP_200_OK,
        )