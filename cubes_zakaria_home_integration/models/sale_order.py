from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    zakaria_so_id = fields.Char()
    Zakaria_state = fields.Char()



class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    zakaria_so_line_id = fields.Char()
