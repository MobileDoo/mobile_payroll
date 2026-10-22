# Mobile Payroll

![Odoo 18.0](https://img.shields.io/badge/Odoo-18.0-714B67) ![License LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue) ![Version 18.0.1.0.0](https://img.shields.io/badge/version-18.0.1.0.0-informational)

> Payslips of employees in the MobileDoo app (Odoo Enterprise payroll or OCA payroll).

Odoo 18 addon of [MobileDoo](https://github.com/MobileDoo) (`mobile_payroll`).

## Overview

Payslips in the MobileDoo app. Employees read their own confirmed payslips; payroll officers look up everybody's. The addon is
**optional**: install it once the company runs payroll in Odoo, with **Odoo Enterprise `hr_payroll`** or the free **OCA `payroll`**
(both keep payslips in `hr.payslip`). Without a payroll module it does nothing, and the `payroll` feature simply does not appear.

## Features

- **My payslips**: period, net pay, earnings and deductions, only for confirmed payslips (`done`, `paid`), never drafts or refunds.
- **All payslips** for payroll officers, filtered by year and searchable, under their normal Odoo rights.
- Detail lines in payslip order with their kind (`earning`, `deduction`, `gross`, `net`, `other`); company-cost lines (`COMP`) and lines
  that do not appear on the payslip are left out.
- **Push** "New payslip" when a payslip is confirmed. The amount is never part of the notification. A scheduled action runs every 15
  minutes; payslips that existed before the module was installed are not announced.

## Requirements

| | |
|---|---|
| Odoo | 18.0 (Community or Enterprise) |
| Odoo modules | `hr` |
| MobileDoo addons | [`mobile_connector`](https://github.com/MobileDoo/mobile_connector/tree/18.0) (same branch) |
| Client | the [MobileDoo](https://github.com/MobileDoo) app for Android and iPhone |

This branch targets **Odoo 18** only; use the branch of your Odoo version.

## Installation

```bash
git clone --branch 18.0 https://github.com/MobileDoo/mobile_payroll.git
git clone --branch 18.0 https://github.com/MobileDoo/mobile_connector.git
# add the cloned folders to addons_path in odoo.conf, then:
odoo -d <database> -i mobile_payroll --stop-after-init
```

The addon is the `mobile_payroll/` folder at the root of the repository, so the repository folder itself can go on `addons_path`.

`mobile_payroll` is **not** installed automatically: install it from *Apps* where the company needs it.

To upgrade after pulling a newer version: `odoo -d <database> -u mobile_payroll --stop-after-init`.

## How it works

| Endpoint | Request | Response |
|---|---|---|
| `/payroll/list` | `{"scope": "mine" | "all", "offset"?, "limit"?, "query"?, "year"?}` | `{records: [Payslip], total}` |
| `/payroll/get` | `{"id"}` | `Payslip` + `lines` + `gross` |

`Payslip`: `id`, `name`, `number`, `employee_id`, `date_from`, `date_to`, `state`, `state_label`, `net` (`null` when the payroll
system has no NET line) and `currency` (`symbol`, `position`, `decimals`).

Models: `mobile.payroll.service` (queries and serialisation) and `mobile.payroll.notice` (remembers which payslips were announced so a
payslip is pushed once).

### Capabilities

| Capability | Granted when |
|---|---|
| `view` | the user has a linked employee (and `hr.payslip` exists) |
| `manage` | the user is a payroll officer or manager (OCA or Enterprise groups) |

## Security

- Employees do not have read access to `hr.payslip` in either payroll system, so `mine` reads with `sudo()` **after** checking that
  the payslip belongs to the caller's employee; the ownership check lives in the search domain.
- `all` runs with the caller's own rights, so Odoo's record rules and companies apply.
- A payslip that does not exist and a payslip of somebody else both answer `403`, so nothing leaks.
- `mobile.payroll.notice` is restricted to system administrators.

## Contributing

Issues and pull requests are welcome. Open pull requests against the branch of the Odoo version you are fixing (this one is `18.0`) and
keep the change inside the `mobile_payroll/` folder.

These repositories are published from MobileDoo's development repository, which remains the source of truth. A merged pull request is
taken back there, and the branches of the other Odoo versions are updated by the maintainers, so a fix is usually welcome even if you can
only test it on one version. `README.md` and `LICENSE` are generated at each release; changes to them are not carried back.

## License

LGPL-3: see [LICENSE](LICENSE).
