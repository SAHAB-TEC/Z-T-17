from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


def round_down_to_nearest_k(number, k):
    return (number // k) * k


def get_target_commission(sales_amount, target_amount, k_target_amount):
    return (sales_amount / target_amount) * k_target_amount


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    last_attendance_id = fields.Many2one(related='employee_id.last_attendance_id', readonly=True,
                                         groups="point_of_sale.group_pos_user")

    target = fields.Float(string='Target', related="employee_id.target", readonly=True)
    refund_limit = fields.Float(string='Refund Limit', related="employee_id.refund_limit", readonly=True)
    total_pos_sales = fields.Float(string='Total POS Sales', related="employee_id.total_pos_sales", readonly=True)
    pos_order_ids = fields.One2many('pos.order', 'pos_employee_id', string='POS Orders',
                                    related="employee_id.pos_order_ids",
                                    readonly=True)
    commission = fields.Float(string='Commission', related="employee_id.commission", readonly=True)
    target_commission = fields.Float(string="Target Commission", related="employee_id.target_commission", readonly=True)
    total_employee_commission = fields.Float(string="Total Employee Commission", related="employee_id.total_employee_commission",
                                             readonly=True)
    is_target = fields.Boolean(related="employee_id.is_target", readonly=True)
    total_employee_pos_sales = fields.Float(string='Total POS Sales', default=0.0, related="employee_id.total_employee_pos_sales",
                                            readonly=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    target = fields.Float(string='Target', related="contract_id.target_amount", store=True)
    refund_limit = fields.Float(string='Refund Limit', related="contract_id.refund_limit", store=True)
    total_pos_sales = fields.Float(string='Total POS Sales', compute='_compute_total_pos_sales')
    pos_order_ids = fields.One2many('pos.order', 'employee_id', string='POS Orders')
    commission = fields.Float(string='Commission', compute='_compute_commission', readonly=True)
    target_commission = fields.Float(string="Target Commission")
    total_employee_commission = fields.Float(string="Total Employee Commission")
    is_target = fields.Boolean(compute='_onchange_is_target')
    total_employee_pos_sales = fields.Float(string='Total POS Sales', compute='_compute_total_employee_pos_sales',
                                            default=0.0)

    def _compute_total_pos_sales(self):  # employee
        for employee in self:
            total_sales = sum(employee.pos_order_ids.filtered(lambda x: x.amount_total >= 0).mapped('amount_total'))
            refund_sales = sum(
                employee.pos_order_ids.filtered(lambda x: x.amount_total < 0).mapped('amount_total')) * -1
            if refund_sales > employee.refund_limit:
                total_sales -= refund_sales
            employee.total_pos_sales = total_sales

    def _compute_total_employee_pos_sales(self):  # manager
        for employee in self:
            total_sales = sum(employee.pos_order_ids.filtered(lambda x: x.amount_total >= 0).mapped('amount_total'))
            refund_sales = sum(
                employee.pos_order_ids.filtered(lambda x: x.amount_total < 0).mapped('amount_total')) * -1
            for child in self.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)]):
                total_sales += child.total_employee_pos_sales
            if refund_sales > employee.refund_limit:
                total_sales -= refund_sales
            print("total_sales ", total_sales)
            employee.total_pos_sales = total_sales
            employee.total_employee_pos_sales = total_sales
            employee._compute_commission()

    @api.depends('target', 'total_pos_sales', 'total_employee_pos_sales')
    def _onchange_is_target(self):
        for emp in self:
            emp.is_target = (
                                        emp.total_pos_sales >= emp.target or emp.total_employee_pos_sales >= emp.target) and emp.target > 0

    @api.depends('total_pos_sales', 'is_target', 'parent_id', 'total_employee_pos_sales', 'contract_id')
    def _compute_commission(self):
        for employee in self:
            employee.target_commission = 0
            total_sales = employee.total_pos_sales if employee.parent_id else employee.total_employee_pos_sales
            if total_sales > employee.contract_id.target_amount:
                if employee.contract_id.rate > 0 and total_sales > 0:
                    net = total_sales - employee.contract_id.target_amount
                    total_rate = net * employee.contract_id.commission_rate / employee.contract_id.rate
                    employee.commission = total_rate
            if total_sales > employee.contract_id.target_amount:
                employee.target_commission = employee.contract_id.each_k_target_amount
                total_sales -= employee.contract_id.target_amount

            else:
                employee.commission = 0

            employee.total_employee_commission = employee.target_commission + employee.commission
