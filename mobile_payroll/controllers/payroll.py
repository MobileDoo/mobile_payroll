from odoo import http
from odoo.http import request

from odoo.addons.mobile_connector.controllers.utils import MobileApiError, mobile_route, require_access

SCOPES = {'mine': 'view', 'all': 'manage'}


class MobilePayrollController(http.Controller):

    @mobile_route('/mobile/api/v1/payroll/list')
    def payroll_list(self, payload):
        scope = payload.get('scope') or 'mine'
        capability = SCOPES.get(scope)
        if not capability:
            raise MobileApiError('bad_request', f'scope must be one of {", ".join(SCOPES)}')
        require_access('payroll', capability)
        try:
            year = int(payload['year']) if payload.get('year') else None
        except (TypeError, ValueError):
            raise MobileApiError('bad_request', 'year must be a number')
        return request.env['mobile.payroll.service']._mobile_list(
            scope,
            offset=max(int(payload.get('offset') or 0), 0),
            limit=max(int(payload.get('limit') or 40), 1),
            query=payload.get('query'),
            year=year,
        )

    @mobile_route('/mobile/api/v1/payroll/get')
    def payroll_get(self, payload):
        require_access('payroll')
        try:
            payslip_id = int(payload['id'])
        except (KeyError, TypeError, ValueError):
            raise MobileApiError('bad_request', 'id is required')
        return request.env['mobile.payroll.service']._mobile_get(payslip_id)
