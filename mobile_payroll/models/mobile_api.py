from odoo import _, api, models


class MobileApi(models.AbstractModel):
    _inherit = 'mobile.api'

    @api.model
    def _mobile_features(self):
        features = super()._mobile_features()
        # The module can be installed before the company chooses a payroll: no payslips, no feature.
        return features + ['payroll'] if 'hr.payslip' in self.env else features

    @api.model
    def _mobile_access(self):
        access = super()._mobile_access()
        service = self.env['mobile.payroll.service']
        if 'hr.payslip' not in self.env or self.env.user.share:
            return access
        capabilities = {
            # Own payslips: any employee with a linked user (read with sudo after the ownership check).
            'view': bool(self.env.user.employee_id),
            'manage': service._mobile_is_officer(),
        }
        if any(capabilities.values()):
            access['payroll'] = capabilities
        return access

    @api.model
    def _mobile_home_tiles(self):
        return super()._mobile_home_tiles() + [
            {'key': 'payroll', 'label': _('Payslips'), 'feature': 'payroll', 'capability': 'view', 'sequence': 70},
            {'key': 'payroll_all', 'label': _('All payslips'), 'feature': 'payroll', 'capability': 'manage',
             'sequence': 71},
        ]

    @api.model
    def _mobile_home_tabs(self):
        return super()._mobile_home_tabs() + [
            {'key': 'payroll', 'label': _('Payslips'), 'feature': 'payroll', 'capability': 'view', 'sequence': 90},
        ]
