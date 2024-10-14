from odoo import models, fields, api


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    category_id = fields.Many2one('product.category', string="Category", related="product_id.categ_id", store=True)
