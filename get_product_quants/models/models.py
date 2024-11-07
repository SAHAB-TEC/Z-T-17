from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    text = fields.Text('الكميات فى المخازن', compute='_get_text')

    @api.depends('product_id')
    def _get_text(self):
        for rec in self:
            quants = rec.product_id.stock_quant_ids
            text = ''
            if quants:
                for quant in quants:
                    if quant.location_id.usage == 'internal':
                        text = text + quant.location_id.name + '  ' + str(quant.quantity) + '\n'
            rec.text = text
