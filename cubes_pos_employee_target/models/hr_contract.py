from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    target_amount = fields.Float(string='Total Target Sales Amount')
    each_k_target_amount = fields.Float(string='Amount per Thousand (k)')
    commission_rate = fields.Float(string='Commission Rate')
    rate = fields.Float(string='Rate')
    refund_limit = fields.Float(string='Refund Limit')
