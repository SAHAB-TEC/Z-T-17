
from odoo import api, models,fields,_
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    discount_amount = fields.Float(
        string="Discount Amount",
        store=True, readonly=False)
    