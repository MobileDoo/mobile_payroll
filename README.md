# Mobile Payroll (`mobile_payroll`)

Payslips of employees in the MobileDoo app (Odoo Enterprise payroll or OCA payroll).

Odoo addon for [MobileDoo](https://github.com/MobileDoo), the mobile app for Odoo. This branch (`19.0`) is for **Odoo 19**; every supported Odoo version has its own branch with the same addon name.

## Installation

Requires [`mobile_connector`](https://github.com/MobileDoo/mobile_connector) (same branch) and the Odoo module(s) `hr`.

Add this repository to `addons_path` (the addon is the `mobile_payroll/` folder at the root) and install `mobile_payroll` from *Apps*, or:

```bash
odoo -d <database> -i mobile_payroll --stop-after-init
```

## License

LGPL-3 - see [LICENSE](LICENSE).
