from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # TODO: Not working on odoo 16
    def _get_allowance(self, employee):
        if employee.is_manager:
            return (employee.total_pos_sales / 1000) * employee.contract_id.each_k_target_amount
        else:
            if employee.total_pos_sales > employee.contract_id.target_amount:
                return employee.contract_id.target_amount
            else:
                return 0

    def _get_rules(self):
        rules = super(HrPayslip, self)._get_rules()
        rules.append(('Allowance', self._get_allowance))
        return rules

    def compute_sheet(self):
        for payslip in self:
            super(HrPayslip, payslip).compute_sheet()
            if payslip.employee_id.is_target:
                commission = payslip.employee_id.commission
                line_values = {
                    'name': self.env.ref('cubes_pos_employee_target.hr_rule_commission_target').name,
                    'quantity': 1,
                    'rate': 100,
                    'salary_rule_id': self.env.ref('cubes_pos_employee_target.hr_rule_commission_target').id,
                    'code': self.env.ref('cubes_pos_employee_target.hr_rule_commission_target').code,
                    'amount': commission,
                }
                payslip.write({
                    'line_ids': [(0, 0, line_values)]
                })
