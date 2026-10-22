{
    'name': 'Mobile Payroll',
    'version': '19.0.1.0.0',
    'summary': 'Payslips of employees in the MobileDoo app (Odoo Enterprise payroll or OCA payroll)',
    'description': """
Optional: install it once the company runs payroll in Odoo, with Odoo Enterprise's `hr_payroll` or the free
OCA `payroll` (both keep payslips in `hr.payslip`). Without payroll the module does nothing.

* Employees read their confirmed payslips: period, net pay, earnings and deductions.
* Payroll officers search the payslips of everybody (their own Odoo rights apply).
* A push tells the employee when a new payslip is confirmed.
""",
    'category': 'Human Resources/Payroll',
    'author': 'MobileDoo',
    'license': 'LGPL-3',
    'depends': ['mobile_connector', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
}
