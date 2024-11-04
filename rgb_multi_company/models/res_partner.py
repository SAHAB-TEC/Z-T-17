# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_sequence = fields.Char(string='Customer Sequence', required=True, copy=False, readonly=True, index=True, default='New', store=True)

    @api.model_create_multi
    def create(self, vals):

        for vals in vals:
            if 'customer_sequence' not in vals or vals['customer_sequence'] == _('New'):
                vals['customer_sequence'] = self.env['ir.sequence'].next_by_code('res.partner.customer.sequence') or _('New')

        return super().create(vals)