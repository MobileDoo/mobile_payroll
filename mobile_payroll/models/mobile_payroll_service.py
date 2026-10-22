"""Payslips on mobile: employees read theirs, payroll officers everybody's.

`hr.payslip` comes from Odoo Enterprise (`hr_payroll`) or the OCA `payroll` module, with the same fields where it
matters here (employee, period, state, lines with a category and a total). Employees have no access right on payslips
in either, so their own are read with `sudo()` after checking whose they are and that they are confirmed; officers
read through their own rights (record rules, companies). Draft payslips of HR are never shown to the employee.
"""
from odoo import _, api, fields, models
from odoo.exceptions import AccessError

# Confirmed payslips: Odoo Enterprise adds "paid" to "done".
CONFIRMED = ('done', 'paid')
# Officer groups: Odoo Enterprise, then OCA payroll.
OFFICER_GROUPS = ('hr_payroll.group_hr_payroll_user', 'payroll.group_payroll_user')
# What a line is for the employee: the category code of the salary rule.
KINDS = {'BASIC': 'earning', 'ALW': 'earning', 'GROSS': 'gross', 'DED': 'deduction', 'NET': 'net'}
HIDDEN_CATEGORIES = ('COMP',)  # what the company pays on top (contributions): not part of the employee's slip
MAX_LIMIT = 100


class MobilePayrollService(models.AbstractModel):
    _name = 'mobile.payroll.service'
    _description = 'Mobile Payroll Service'

    @api.model
    def _mobile_is_officer(self):
        user = self.env.user
        for xmlid in OFFICER_GROUPS:
            if self.env.ref(xmlid, raise_if_not_found=False) and user.has_group(xmlid):
                return True
        return False

    @api.model
    def _visible_states(self):
        keys = {key for key, _label in self.env['hr.payslip']._fields['state']._description_selection(self.env)}
        return [state for state in CONFIRMED if state in keys]

    # ------------------------------------------------------------------
    # Who may read what
    # ------------------------------------------------------------------

    @api.model
    def _domain(self, scope, query=None, year=None):
        Payslip = self.env['hr.payslip']
        if scope == 'mine':
            domain = [('employee_id.user_id', '=', self.env.uid), ('state', 'in', self._visible_states())]
            if 'credit_note' in Payslip._fields:
                domain.append(('credit_note', '=', False))
        else:
            domain = []
        if isinstance(query, str) and query.strip():
            text = query.strip()
            domain += ['|', '|', ('employee_id.name', 'ilike', text), ('number', 'ilike', text), ('name', 'ilike', text)]
        if year:
            domain += [('date_from', '>=', f'{int(year)}-01-01'), ('date_from', '<=', f'{int(year)}-12-31')]
        return domain

    @api.model
    def _payslips(self, scope):
        """The model to search for a scope: own payslips with sudo (ownership is in the domain), the rest with rights."""
        Payslip = self.env['hr.payslip']
        return Payslip.sudo() if scope == 'mine' else Payslip

    @api.model
    def _readable(self, payslip_id):
        """The payslip if the user may read it, else an AccessError (the same as the web)."""
        slip = self.env['hr.payslip'].sudo().browse(payslip_id).exists()
        if not slip:
            raise AccessError(_('This payslip does not exist.'))
        own = slip.employee_id.user_id == self.env.user and slip.state in self._visible_states()
        if own and ('credit_note' not in slip._fields or not slip.credit_note):
            return slip
        # Anybody else's: the user's own rights decide.
        slip = self.env['hr.payslip'].browse(payslip_id)
        if hasattr(slip, 'check_access'):
            slip.check_access('read')
        else:  # Odoo 17
            slip.check_access_rights('read')
            slip.check_access_rule('read')
        return slip.sudo()

    # ------------------------------------------------------------------
    # What is sent
    # ------------------------------------------------------------------

    @api.model
    def _net(self, slip):
        if 'net_wage' in slip._fields:  # Odoo Enterprise
            return slip.net_wage
        net = slip.line_ids.filtered(lambda line: line.code == 'NET')
        return sum(net.mapped('total')) if net else None

    @api.model
    def _state_label(self, slip):
        return dict(slip._fields['state']._description_selection(self.env)).get(slip.state, slip.state)

    @api.model
    def _currency(self, slip):
        currency = slip.company_id.currency_id
        return {'symbol': currency.symbol, 'position': currency.position, 'decimals': currency.decimal_places}

    @api.model
    def _serialize(self, slip):
        return {
            'id': slip.id,
            'name': slip.name or slip.number or '',
            'number': slip.number or False,
            'employee_id': [slip.employee_id.id, slip.employee_id.name],
            'date_from': fields.Date.to_string(slip.date_from),
            'date_to': fields.Date.to_string(slip.date_to),
            'state': slip.state,
            'state_label': self._state_label(slip),
            'net': self._net(slip),
            'currency': self._currency(slip),
        }

    @api.model
    def _lines(self, slip):
        lines = slip.line_ids.sorted(lambda line: (line.sequence, line.id))
        if 'appears_on_payslip' in lines._fields:
            lines = lines.filtered('appears_on_payslip')
        result = []
        for line in lines:
            category = line.category_id.code or ''
            if category in HIDDEN_CATEGORIES:
                continue
            result.append({
                'id': line.id, 'code': line.code or '', 'name': line.name, 'category': category,
                'kind': KINDS.get(category, 'other'), 'total': line.total,
            })
        return result

    @api.model
    def _mobile_list(self, scope, offset=0, limit=40, query=None, year=None):
        domain = self._domain(scope, query, year)
        Payslip = self._payslips(scope)
        records = Payslip.search(domain, offset=offset, limit=min(limit, MAX_LIMIT), order='date_from desc, id desc')
        return {'records': [self._serialize(slip) for slip in records], 'total': Payslip.search_count(domain)}

    @api.model
    def _mobile_get(self, payslip_id):
        slip = self._readable(payslip_id)
        data = self._serialize(slip)
        lines = self._lines(slip)
        data['lines'] = lines
        data['gross'] = next((line['total'] for line in lines if line['kind'] == 'gross'), None)
        return data
