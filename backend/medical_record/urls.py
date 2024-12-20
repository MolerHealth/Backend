from django.urls import path
from .views import (
    MedicalRecordListCreateView,
    MedicalRecordRetrieveUpdateView,
    MedicalRecordVersionsView,
    MedicalRecordSpecificVersionView,
    RequestPermissionView,
    RespondToPermissionRequestView,
    DeletePermissionRequestsToPatientView
    
)

urlpatterns = [
    path('medical-records/', MedicalRecordListCreateView.as_view(), name='medical-record-list-create'),  # List all latest records or create a new one
    path('medical-records/<int:pk>/', MedicalRecordRetrieveUpdateView.as_view(), name='medical-record-detail'),  # Retrieve, update (create new version), or delete a record
    path('medical-records/<int:pk>/versions/', MedicalRecordVersionsView.as_view(), name='medical-record-versions'),  # List all versions of a record
    path('medical-records/<int:pk>/version/<int:version_number>/', MedicalRecordSpecificVersionView.as_view(), name='medical-record-specific-version'),  # Retrieve a specific version by version number
    
    path('medical-record/request-permission/', RequestPermissionView.as_view(), name='request_permission'),
    path('medical-record/permission-request/respond/', RespondToPermissionRequestView.as_view(), name='respond_permission'),
    
     path('medical-record/delete-requests-to-patient/', DeletePermissionRequestsToPatientView.as_view(), name='delete_permission_requests_to_patient',),
]
