from odoo import fields, models, api, _


class HRPayroll(models.Model):
    _inherit = 'hr.payslip'

    total_commission = fields.Float(
        string='Employee Commission Amount',
        required=False)

    skip_deduction = fields.Boolean(
        string='Do You Need To Skip Calculate for this Month ?',
        required=False)

    def compute_sheet(self):
        for rec in self:
            rec.total_commission = rec.employee_id.total_employee_commission if not rec.skip_deduction else 0
        res = super(HRPayroll, self).compute_sheet()
        return res

    def action_payslip_paid(self):
        for rec in self:
            pos_status = rec.employee_id.pos_order_ids
            for pos in pos_status:
                pos.write({'payslip_status': True})
        res = super(HRPayroll, self).action_payslip_paid()
        return res
