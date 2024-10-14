from datetime import datetime, timedelta
from odoo import _, api, fields, models , tools
from odoo.exceptions import UserError


class RequestLeave(models.Model):
    _name = 'leave.request.employee'
    _description = 'Employee Leave Request'

    name = fields.Char()

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee Name',
        required=False)
    contract_id = fields.Many2one(
        comodel_name='hr.contract',
        string='Contract',
        related="employee_id.contract_id",
        required=False)
    request_from = fields.Datetime(
        string='Request From',
        required=True)
    request_to = fields.Datetime(
        string='Request To',
        required=True)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('confirm', 'Confirmed'),
                   ('done', 'Done'), ],default="draft",
        required=False, )

    total_leave_hours = fields.Float(
        string='Total Hours',
        compute="action_return_diff",
        store=True,
        required=False)

    reason_to_leave = fields.Text(
        string="Reason To Leave",
        required=False)

    def action_confirm(self):
        for rec in self:
            if rec.request_to < rec.request_from:
                raise UserError(_("Request to Must be Bigger than request from"))
            else:
                return rec.write({"state": "confirm"})

    def action_draft(self):
        for rec in self:
            return rec.write({"state": "draft"})

    def action_validate(self):
        for rec in self:
            return rec.write({"state": "done"})

    @api.depends("request_to", "request_from")
    def action_return_diff(self):
        for rec in self:
            from_date = rec.request_from
            to_date = rec.request_to
            if from_date and to_date:
                diff = to_date - from_date
                float_diff = diff.total_seconds() / 3600
                rec.total_leave_hours = float_diff
            else:rec.total_leave_hours = 0





