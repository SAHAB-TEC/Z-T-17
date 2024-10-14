from odoo import fields, models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        res += ['hr.employee']
        return res

    def _loader_params_pos_order(self):
        res = super()._loader_params_pos_order()
        print("LLL", res)
        return res

    def _loader_params_hr_employee(self):
        return {
            'search_params': {
                'fields': ['name']
            }
        }

    def _get_pos_ui_hr_employee(self, params):
        return self.env['hr.employee'].search(**params['search_params'])


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_employee_id = fields.Many2one('hr.employee', string="POS Employee")

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['pos_employee_id'] = ui_order.get('pos_employee_id')
        return res

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        res['pos_employee_id'] = order.pos_employee_id
        return res