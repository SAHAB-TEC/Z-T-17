# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _description = _('ProductCategory')

    company_id = fields.Many2one('res.company', 'Company')