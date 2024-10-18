# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_cost_hide = fields.Boolean(
        string='Price Cost Hide',
        compute='_compute_price_cost_hide',
        required=False, store=False)

    qty_available = fields.Char()

    def _compute_price_cost_hide(self):
        for rec in self:
            if rec.env.user.has_group("product_price_group_ah.group_restrict_standard_price"):
                rec.price_cost_hide = True
            else:
                rec.price_cost_hide = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    price_cost_hide = fields.Boolean(
        string='Price Cost Hide',
        compute='_compute_price_cost_hide',
        required=False, store=False)

    def _compute_price_cost_hide(self):
        for rec in self:
            if rec.env.user.has_group("product_price_group_ah.group_restrict_standard_price"):
                rec.price_cost_hide = True
            else:
                rec.price_cost_hide = False
