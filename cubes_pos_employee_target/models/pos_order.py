from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_employee_id = fields.Many2one('hr.employee', string="POS Employee")
    payslip_status = fields.Boolean(
        string='Is Employee Commission Paid ?',
        required=False)

    @api.model
    def _order_fields(self, ui_order):
        print(ui_order)
        res = super()._order_fields(ui_order)
        if ui_order.get('pos_employee_id') != 'null':
            res['pos_employee_id'] = ui_order.get('pos_employee_id') or False
        return res

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        res['pos_employee_id'] = order.pos_employee_id
        return res