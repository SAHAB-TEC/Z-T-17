from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    zakaria_id = fields.Char(string="Zakaria ID")


class ProductTempletInherit(models.Model):
    _inherit = 'product.template'

    zakaria_id = fields.Char(string="Zakaria ID")

    @api.model
    def create(self, values):
        res = super(ProductTempletInherit, self).create(values)
        for rec in res:
            url = "https://integration.zakariahome.com/api/odoo"
            data = {
                "productId": rec.id,
                "barcode": rec.barcode,
                "quantity": rec.qty_available,
                "price": rec.list_price,
                "warehouseId": rec.warehouse_id.id,
                "action": 'product updated',
            }
            headers = {
                'header-key': 'siyool_auth',
                'header-value': 'ljslkfwlkfjwdsouhuwhf$#%#kjfhk#$^$#lkjfw',
                'siyool_auth': 'ljslkfwlkfjwdsouhuwhf$#%#kjfhk#$^$#lkjfw',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=data)
            _logger.info(response.text)
        return res

    def write(self, vals):
        res = super(ProductTempletInherit, self).write(vals)
        for rec in self:
            url = "https://integration.zakariahome.com/api/odoo"
            data = {
                "productId": rec.id
            }
            if vals.get('barcode'):
                data["barcode"] = vals['barcode']
            else:
                data["barcode"] = rec.barcode
            if vals.get('qty_available'):
                data["quantity"] = vals['qty_available']
            else:
                data["quantity"] = rec.qty_available
            if vals.get('list_price'):
                data["price"] = vals['list_price']
            else:
                data["price"] = rec.list_price
            if vals.get('warehouse_id'):
                data["warehouseId"] = vals['warehouse_id'].id
            else:
                data["warehouseId"] = rec.warehouse_id.id
            data["action"] = 'product updated'
            headers = {
                'header-key': 'siyool_auth',
                'header-value': 'ljslkfwlkfjwdsouhuwhf$#%#kjfhk#$^$#lkjfw',
                'siyool_auth': 'ljslkfwlkfjwdsouhuwhf$#%#kjfhk#$^$#lkjfw',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=data)
            _logger.info(response.text)
        return res


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    zakaria_inv_id = fields.Char()
    Zakaria_state = fields.Char()
