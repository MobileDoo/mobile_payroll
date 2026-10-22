from . import controllers, models


def post_init_hook(env):
    """Payslips confirmed before the module came are old news: no push for them."""
    env['mobile.payroll.notice']._mark_existing()
