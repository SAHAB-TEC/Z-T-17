from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    target_amount = fields.Float(string='Target Amount')
    each_k_target_amount = fields.Float(string='Amount per Thousand (k)')
