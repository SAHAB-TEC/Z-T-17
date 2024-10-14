# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
import pprint

class PosReportAction(models.AbstractModel):
    _inherit  = "pos.session"


    def get_payment_by_group(self):
        paymnents = self.env['pos.payment'].search([('session_id','=',self.id)])
        payment_dict = {}
        for elem in paymnents:
            payment_dict.setdefault(elem.payment_method_id.name,{'name':self.name,
                                                                 'journal_id':elem.payment_method_id.journal_id.name,
                                                                  'currency_id':elem.currency_id.name,
                                                                  'amount':0})
            payment_dict[elem.payment_method_id.name]['amount']+=elem.amount
        return payment_dict

    def get_session_cashiers(self):
        orders = self.env['pos.order'].search([('session_id','=',self.id)])
        cashiers = set()
        try:
            for elem in orders:
                cashiers.add(str(elem.cashier))

            names = ''
            for cash in cashiers:
                names+=cash+', '

            if names:
                names = names[:-2]
            return names

        except: # in case there is no pos_hr installed
            return self.user_id.name


class PosReportAction(models.AbstractModel):
    _name = "report.sr_print_pos_session.pos_session_report_template"
    _description = 'pos_session_report_template'

    def _get_report_values(self, docids, data=None):
        doc = self.env['pos.session'].search([('id','in',docids)])

        return {'docs':doc}