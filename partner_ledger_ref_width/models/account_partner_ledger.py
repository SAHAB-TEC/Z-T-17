# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.AbstractModel):
    _inherit = "account.report"

    def _get_columns_name(self, options):
        columns = [
            {'style': 'width: 1%'},
            {'name': _('JRNL'), 'style': 'width:5%'},
            {'name': _('Account'), 'style': 'width:5%'},
            {'name': _('Ref'), 'style': 'width:200px; display: block;'},
            {'name': _('Due Date'),'style': 'width:0%; display: none'},
            {'name': _('Matching Number'), 'style': 'width:0%; display: none'},
            {'name': _('Initial Balance'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
        ]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns