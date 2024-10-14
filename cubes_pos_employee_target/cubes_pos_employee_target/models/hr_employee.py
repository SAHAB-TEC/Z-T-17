from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    target = fields.Float(string='Target')
    refund_limit = fields.Float(string='Refund Limit')
    total_pos_sales = fields.Float(string='Total POS Sales', compute='_compute_total_pos_sales')
    pos_order_ids = fields.One2many('pos.order', 'pos_employee_id', string='POS Orders')
    commission = fields.Float(string='Commission', compute='_compute_commission', readonly=True)
    commission_rate = fields.Float(string='Commission Rate')
    rate = fields.Float(string='Rate')
    is_target = fields.Boolean(compute='_onchange_is_target')
    total_employee_pos_sales = fields.Float(string='Total POS Sales', compute='_compute_total_employee_pos_sales',
                                            default=0.0)

    @api.depends('pos_order_ids', 'refund_limit')  # for employee
    def _compute_total_pos_sales(self):
        for employee in self:
            total_sales = sum(order.amount_total for order in employee.pos_order_ids if order.amount_total >= 0)
            if total_sales > employee.refund_limit:
                total_sales -= sum(order.amount_total for order in employee.pos_order_ids if
                                   order.amount_total < 0 and abs(order.amount_total) > employee.refund_limit)
            employee.total_pos_sales = total_sales

    @api.depends('pos_order_ids', 'refund_limit')  # for manger
    def _compute_total_employee_pos_sales(self):
        for employee in self:
            total_sales = sum(order.amount_total for order in employee.pos_order_ids if order.amount_total >= 0)
            if employee.child_ids:
                for child in employee.child_ids:
                    total_sales += child.total_pos_sales
                if total_sales > employee.refund_limit:
                    total_sales -= sum(order.amount_total for order in employee.pos_order_ids if
                                       order.amount_total < 0 and abs(order.amount_total) > employee.refund_limit)
            employee.total_employee_pos_sales = total_sales

    @api.depends('target', 'total_pos_sales', 'total_employee_pos_sales')
    def _onchange_is_target(self):
        for emp in self:
            emp.is_target = (emp.total_pos_sales >= emp.target or emp.total_employee_pos_sales >= emp.target) and emp.target > 0

    @api.depends('commission_rate', 'rate', 'total_pos_sales')
    def _compute_commission(self):
        for employee in self:
            if employee.is_target:
                if employee.parent_id:  # for employee
                    if employee.rate > 0:
                        total_rate = (employee.total_pos_sales / employee.rate) * employee.commission_rate
                        employee.commission = total_rate
                    else:
                        employee.commission = 0
                else:
                    if employee.rate > 0:  # for manger
                        total_rate = (employee.total_employee_pos_sales / employee.rate) * employee.commission_rate
                        employee.commission = total_rate
                    else:
                        employee.commission = 0
            else:
                employee.commission = 0