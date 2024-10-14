# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('cubes_zakaria_custom.create_product_group'):
            raise ValidationError("Not allowed to create product")
        return super(ProductProduct, self).create(vals)
