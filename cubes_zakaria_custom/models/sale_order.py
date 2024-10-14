from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_has_create(self):
        return self.env.user.has_group(
                'cubes_zakaria_custom.create_product_group')

    total_qty = fields.Float(compute="get_total_qty", store=False, readonly=True, string="الكمية الكلية")
    has_create_product = fields.Boolean(compute='check_has_create_product',default=_check_has_create, store=False)

    @api.depends_context("uid")
    def check_has_create_product(self):
        for rec in self:
            rec.has_create_product = self.env.user.has_group(
                'cubes_zakaria_custom.create_product_group')

    def action_confirm(self):
        for rec in self:
            if rec.order_line and rec.order_line.filtered(lambda x: x.price_unit == 0.0 and not x.display_type):
                raise ValidationError('Not allowed to confirm order has line with zero price')
            return super(SaleOrder, self).action_confirm()

    def get_total_qty(self):
        for elem in self:
            elem.total_qty = 0
            for line in elem.order_line:
                elem.total_qty += line.product_uom_qty


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    serial_number = fields.Integer(compute="get_serial_number", string="ر.ت")

    copy_product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company

    @api.onchange('copy_product_id')
    def _onchange_copy_product_id(self):
        for rec in self:
            if rec.copy_product_id:
                rec.product_id = rec.copy_product_id.id

    def get_serial_number(self):
        i = 1
        for elem in self:
            elem.serial_number = i
            i += 1

    @api.onchange('product_uom_qty')
    def change_so_total_qty(self):
        for elem in self:
            elem.order_id.get_total_qty()
