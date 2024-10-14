# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.constrains('default_code')
    def _check_duplicate_code(self):
        res = self.search([('default_code', '=', self.default_code), ('default_code', '!=', False)])
        if len(res) > 1:
            raise ValidationError(_('Internal Reference must be unique !'))

    @api.onchange('default_code')
    def _onchange_default_code(self):
        if not self.default_code:
            return

        domain = [('default_code', '=', self.default_code)]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        if self.env['product.product'].search(domain, limit=1):
            return


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('default_code')
    def _onchange_default_code(self):
        if not self.default_code:
            return

        domain = [('default_code', '=', self.default_code)]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        if self.env['product.product'].search(domain, limit=1):
            return
