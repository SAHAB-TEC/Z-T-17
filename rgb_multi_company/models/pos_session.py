# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        vals = super()._loader_params_res_partner()
        vals["search_params"]["fields"] += ["customer_sequence"]
        return vals
