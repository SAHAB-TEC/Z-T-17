from itertools import groupby
import math
from odoo import api, models,fields,_
from odoo.fields import float_is_zero
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import UTC
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_amount = fields.Float(
        string="Discount Amount",
        store=True, readonly=False
    )

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount' ,'discount_amount')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = next(iter(tax_results['totals'].values()))
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            if line.discount_amount:
              amount_untaxed =amount_untaxed - (line.discount_amount + (line.discount / 100))
              amount_untaxed = math.ceil(amount_untaxed)
            line.update({
                'price_subtotal': amount_untaxed  ,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })
    
   