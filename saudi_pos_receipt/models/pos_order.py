# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang


class POSOrder(models.Model):
    _inherit = "pos.order"

    amount_untaxed = fields.Float(string="Untaxed Amount",compute="_compute_amount_untaxed")

    def _compute_amount_untaxed(self):
        for order in self:
            currency = order.pricelist_id.currency_id or order.currency_id
            if currency:
                order.amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
