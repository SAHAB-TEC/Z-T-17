# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_qty = fields.Float(compute="get_total_qty",store=False, readonly=True, string="الكمية الكلية")

    @api.depends('order_line.product_qty')
    def get_total_qty(self):
        for elem in self:
            elem.total_qty = 0
            for line in elem.order_line:
                elem.total_qty += line.product_qty



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    serial_number = fields.Integer(compute="get_serial_number", string="ر.ت")
    price_unit = fields.Float(string='Unit Price', required=True, digits=[12,4])

    
    def get_serial_number(self):
        i=1
        for elem in self:
            elem.serial_number = i
            i+=1

    @api.onchange('product_qty')
    def change_so_total_qty(self):
        for elem in self:
            elem.order_id.get_total_qty()



