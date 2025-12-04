"""
API views for report generation and export.
"""
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import HttpResponse
from .services import ReportService
from .exporters import ExcelExporter, CSVExporter, PDFExporter
from .export_import_service import OrganizationExportImportService


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating and exporting reports.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_service = None

    def get_report_service(self):
        """Get or create report service instance."""
        if self.report_service is None:
            self.report_service = ReportService(self.request.user)
        return self.report_service

    @action(detail=False, methods=['post'], url_path='organization')
    def organization_report(self, request):
        """
        Generate a comprehensive organization report.

        POST /api/reports/organization/
        Body:
        {
            "organization_id": "uuid",
            "include_sections": ["locations", "contacts", "network_devices", ...],
            "format": "json|excel|csv|pdf"
        }
        """
        organization_id = request.data.get('organization_id')
        include_sections = request.data.get('include_sections')
        export_format = request.data.get('format', 'json')

        if not organization_id:
            return Response(
                {'error': 'organization_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = self.get_report_service()
            report_data = service.generate_organization_report(
                organization_id=organization_id,
                include_sections=include_sections
            )

            if export_format == 'json':
                return Response(report_data)
            elif export_format == 'excel':
                return self._export_to_excel(report_data, 'organization_report')
            elif export_format == 'csv':
                return self._export_to_csv(report_data, 'organization_report')
            elif export_format == 'pdf':
                return self._export_to_pdf(report_data, 'organization_report')
            else:
                return Response(
                    {'error': f'Invalid format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='location')
    def location_report(self, request):
        """
        Generate a comprehensive location report.

        POST /api/reports/location/
        Body:
        {
            "location_id": "uuid",
            "include_sections": ["contacts", "network_devices", ...],
            "format": "json|excel|csv|pdf"
        }
        """
        location_id = request.data.get('location_id')
        include_sections = request.data.get('include_sections')
        export_format = request.data.get('format', 'json')

        if not location_id:
            return Response(
                {'error': 'location_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = self.get_report_service()
            report_data = service.generate_location_report(
                location_id=location_id,
                include_sections=include_sections
            )

            if export_format == 'json':
                return Response(report_data)
            elif export_format == 'excel':
                return self._export_to_excel(report_data, 'location_report')
            elif export_format == 'csv':
                return self._export_to_csv(report_data, 'location_report')
            elif export_format == 'pdf':
                return self._export_to_pdf(report_data, 'location_report')
            else:
                return Response(
                    {'error': f'Invalid format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='asset-inventory')
    def asset_inventory(self, request):
        """
        Generate an asset inventory report.

        POST /api/reports/asset-inventory/
        Body:
        {
            "organization_id": "uuid",  // optional
            "location_id": "uuid",      // optional
            "format": "json|excel|csv|pdf"
        }
        """
        organization_id = request.data.get('organization_id')
        location_id = request.data.get('location_id')
        export_format = request.data.get('format', 'json')

        try:
            service = self.get_report_service()
            report_data = service.generate_asset_inventory_report(
                organization_id=organization_id,
                location_id=location_id
            )

            if export_format == 'json':
                return Response(report_data)
            elif export_format == 'excel':
                return self._export_to_excel(report_data, 'asset_inventory')
            elif export_format == 'csv':
                return self._export_to_csv(report_data, 'asset_inventory')
            elif export_format == 'pdf':
                return self._export_to_pdf(report_data, 'asset_inventory')
            else:
                return Response(
                    {'error': f'Invalid format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='software-licenses')
    def software_licenses(self, request):
        """
        Generate a software license report.

        POST /api/reports/software-licenses/
        Body:
        {
            "organization_id": "uuid",  // optional
            "format": "json|excel|csv|pdf"
        }
        """
        organization_id = request.data.get('organization_id')
        export_format = request.data.get('format', 'json')

        try:
            service = self.get_report_service()
            report_data = service.generate_software_license_report(
                organization_id=organization_id
            )

            if export_format == 'json':
                return Response(report_data)
            elif export_format == 'excel':
                return self._export_to_excel(report_data, 'software_licenses')
            elif export_format == 'csv':
                return self._export_to_csv(report_data, 'software_licenses')
            elif export_format == 'pdf':
                return self._export_to_pdf(report_data, 'software_licenses')
            else:
                return Response(
                    {'error': f'Invalid format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _export_to_excel(self, report_data, report_name):
        """Export report to Excel format."""
        exporter = ExcelExporter()
        excel_file = exporter.export(report_data)

        response = HttpResponse(
            excel_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_name}_{report_data.get("generated_at", "")}.xlsx"'
        return response

    def _export_to_csv(self, report_data, report_name):
        """Export report to CSV format."""
        exporter = CSVExporter()
        csv_file = exporter.export(report_data)

        response = HttpResponse(csv_file, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_name}_{report_data.get("generated_at", "")}.csv"'
        return response

    def _export_to_pdf(self, report_data, report_name):
        """Export report to PDF format."""
        exporter = PDFExporter()
        pdf_file = exporter.export(report_data)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_name}_{report_data.get("generated_at", "")}.pdf"'
        return response

    @action(detail=False, methods=['post'], url_path='export-organizations')
    def export_organizations(self, request):
        """
        Export complete organization data for backup purposes.

        POST /api/reports/export-organizations/
        Body:
        {
            "organization_ids": ["uuid1", "uuid2", ...],  // optional, null/empty = all orgs
            "include_deleted": false  // optional, default false
        }
        """
        organization_ids = request.data.get('organization_ids')
        include_deleted = request.data.get('include_deleted', False)

        try:
            service = OrganizationExportImportService(request.user)
            export_data = service.export_organizations(
                organization_ids=organization_ids,
                include_deleted=include_deleted
            )

            # Return as downloadable JSON file
            response = HttpResponse(
                json.dumps(export_data, indent=2),
                content_type='application/json'
            )
            filename = f'organizations_export_{export_data.get("exported_at", "")}.json'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            return Response(
                {'error': f'Error exporting organizations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        detail=False,
        methods=['post'],
        url_path='import-organizations',
        parser_classes=[MultiPartParser, FormParser, JSONParser]
    )
    def import_organizations(self, request):
        """
        Import organization data from an export file.

        POST /api/reports/import-organizations/
        Body (multipart/form-data):
        {
            "file": <file>,  // JSON file from export
            "overwrite_existing": false,  // optional
            "preserve_ids": false  // optional
        }
        OR Body (application/json):
        {
            "data": {...},  // Export data object
            "overwrite_existing": false,  // optional
            "preserve_ids": false  // optional
        }
        """
        overwrite_existing = request.data.get('overwrite_existing', 'false')
        preserve_ids = request.data.get('preserve_ids', 'false')

        # Convert string booleans to actual booleans
        if isinstance(overwrite_existing, str):
            overwrite_existing = overwrite_existing.lower() == 'true'
        if isinstance(preserve_ids, str):
            preserve_ids = preserve_ids.lower() == 'true'

        # Get import data from either file upload or direct JSON
        if 'file' in request.FILES:
            # Handle file upload
            uploaded_file = request.FILES['file']
            try:
                import_data = json.load(uploaded_file)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid JSON file'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif 'data' in request.data:
            # Handle direct JSON data
            import_data = request.data['data']
        else:
            return Response(
                {'error': 'No import data provided. Include either "file" or "data" in request.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = OrganizationExportImportService(request.user)
            results = service.import_organizations(
                import_data=import_data,
                overwrite_existing=overwrite_existing,
                preserve_ids=preserve_ids
            )

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error importing organizations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
