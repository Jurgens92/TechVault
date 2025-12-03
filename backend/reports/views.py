"""
API views for report generation and export.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .services import ReportService
from .exporters import ExcelExporter, CSVExporter, PDFExporter


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
