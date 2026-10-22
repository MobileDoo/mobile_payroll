import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MobilePayrollNotice(models.Model):
    """Payslips whose employee already got the push (a plain id: `hr.payslip` exists only with a payroll)."""

    _name = 'mobile.payroll.notice'
    _description = 'Payslip Push Sent'
    _log_access = False

    payslip_id = fields.Integer(required=True, index=True)

    _sql_constraints = [('payslip_unique', 'unique(payslip_id)', 'One push per payslip.')]

    @api.model
    def _mark_existing(self):
        if 'hr.payslip' not in self.env:
            return
        states = self.env['mobile.payroll.service']._visible_states()
        self.env.cr.execute(
            'INSERT INTO mobile_payroll_notice (payslip_id) SELECT id FROM hr_payslip WHERE state IN %s '
            'ON CONFLICT DO NOTHING', (tuple(states),))

    @api.model
    def _cron_notify(self):
        """Push to the employee of every payslip confirmed since the last run."""
        if 'hr.payslip' not in self.env:
            return
        states = self.env['mobile.payroll.service']._visible_states()
        self.env.cr.execute(
            'SELECT id FROM hr_payslip WHERE state IN %s AND id NOT IN (SELECT payslip_id FROM mobile_payroll_notice) '
            'ORDER BY id LIMIT 200', (tuple(states),))
        ids = [row[0] for row in self.env.cr.fetchall()]
        for slip in self.env['hr.payslip'].sudo().browse(ids):
            user = slip.employee_id.user_id
            try:
                if user and user.active:
                    title, body = self.with_context(lang=user.lang)._push_text(slip)
                    self.env['mobile.push.message']._enqueue(user, title, body, {
                        'type': 'payroll', 'model': 'hr.payslip', 'res_id': slip.id,
                    })
            except Exception:  # one bad payslip must not stop the others
                _logger.exception('Payslip push failed for %s', slip.id)
            self.create({'payslip_id': slip.id})

    @api.model
    def _push_text(self, slip):
        """Texts in `self.env.lang` (the employee's language). The amount stays in the app, not in a notification."""
        slip = slip.with_context(lang=self.env.lang)
        return _('New payslip'), slip.name or slip.number or ''
