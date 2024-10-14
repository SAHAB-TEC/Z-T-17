from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta, time


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_salary = fields.Float(
        string='Employee Wage',
        compute='_compute_contract_id_wage',
        required=False)

    @api.depends('contract_id')
    def _compute_contract_id_wage(self):
        for rec in self:
            rec.employee_salary = rec.contract_id.wage

    attendance_late_ids = fields.One2many(
        comodel_name='hr.attendance',
        inverse_name='hr_payslip_late_id',
        compute='_compute_attendance_late_ids'
    )

    attendance_early_ids = fields.One2many(
        comodel_name='hr.attendance',
        inverse_name='hr_payslip_early_id',
        compute="_compute_attendance_early_ids"
    )
    attendance_leave_ids = fields.One2many(
        comodel_name='hr.attendance',
        inverse_name='hr_payslip_leave_id',
        compute="_compute_attendance_leave_ids"
    )

    attendance_extra_hours_ids = fields.One2many(
        comodel_name='hr.attendance',
        inverse_name='hr_payslip_extra_hours_id',
        compute="_compute_attendance_extra_hours_ids"
    )

    total_attendance_late = fields.Float(
        string='Total Late ',
        compute='_compute_total_attendance_late',
    )
    total_attendance_cost = fields.Float(
        string='Cost For Late ',
        compute='_compute_total_attendance_late',
    )
    total_leave_hour_cost = fields.Float(
        string='Cost Leave Before Time ',
        compute='_compute_total_attendance_leave',
    )
    total_attendance_early = fields.Float(
        string='Total Early',
        compute='_compute_total_attendance_early'
    )

    total_extra_hours = fields.Float(
        string='Total Extra Hours',
        compute='_compute_total_extra_hours',
    )

    total_absence_per_month = fields.Integer(
        string='Total Absences',
        compute='_compute_total_absence_per_month',
    )
    total_absence_per_month_cost = fields.Integer(
        string='Total Absences',
        compute='_compute_total_absence_per_month_cost',
    )

    def _compute_total_absence_per_month_cost(self):
        for cost in self:
            first = float(self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.absent1'))
            second = float(self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.absent2'))
            third = float(self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.absent3'))
            if cost.total_absence_per_month == 1:
                cost.total_absence_per_month_cost = first
            if cost.total_absence_per_month == 2:
                cost.total_absence_per_month_cost = first + second
            if cost.total_absence_per_month == 3:
                cost.total_absence_per_month_cost = first + second + third
            else:
                cost.total_absence_per_month_cost = cost.total_absence_per_month * cost.contract_id.wage / cost.number_days_per_month if cost.contract_id else 0

    number_hours_per_month = fields.Float(
        string='Hours per Month',
        compute='_compute_number_hours_per_month',
    )

    total_leave_hours_payslip = fields.Float(
        string='Total Leave Before Time',
        compute='_compute_total_attendance_leave',
    )

    number_days_per_month = fields.Integer(
        string='Days per Month',
        compute='_compute_number_days_per_month',
    )

    first_time_absent = fields.Float(
        string='First Time Late',
        required=False
    )
    first_time_absent_cost = fields.Float(
        string='First Time Cost',
        required=False
    )
    second_time_absent = fields.Float(
        string='Second Time Late',
        required=False
    )
    second_time_absent_cost = fields.Float(
        string='Second Time Cost',
        required=False
    )
    third_time_absent = fields.Float(
        string='Third Time Late',
        required=False
    )

    third_time_absent_cost = fields.Float(
        string='Third Time Cost',
        required=False
    )
    total_cost_late = fields.Float(
        string='Total Absent Cost',
        compute="loop_in_attendences_records",
        required=False
    )

    overtime_amount = fields.Float(
        string='Overtime Amount',
        compute="get_employee_overtime_hour",
        required=False)

    @api.depends('contract_id')
    def get_employee_overtime_hour(self):
        for rec in self:
            self._compute_total_extra_hours()
            employee_hour_rate = rec.contract_id.wage / rec.number_days_per_month if rec.contract_id else 0
            rec.overtime_amount = rec.total_extra_hours * employee_hour_rate if rec.total_extra_hours >= 1 else 0

    def GetFloatOvertime(self, target):
        x = '{0:02.0f}:{1:02.0f}'.format(*divmod(target * 60, 60))
        p = x.replace(':', '.')
        result = float(p)
        target = result
        return target

    def loop_in_attendences_records(self):
        for rec in self:
            attendance_ids = rec.env['hr.attendance'].search(
                [('employee_id', '=', rec.employee_id.id)]).filtered(lambda l: l.late > 0.02).mapped('late')
            total_late = []
            for att in attendance_ids:
                result = rec.get_cost_from_setting(att, total_late)
            res = rec.total_cost_late = sum(total_late)

    def get_cost_from_setting(self, att, total):
        for rec in self:
            first_late = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_first_time'))
            second_late = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_second_time'))
            third_late = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_third_time'))
            first_cost = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_first_cost'))
            second_cost = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_second_cost'))
            third_cost = float(rec.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_third_cost'))
            if first_late <= att <= second_late:
                total.append(first_cost)
            elif second_late <= att <= third_late:
                total.append(second_cost)
            elif att >= third_late:
                total.append(third_cost)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_attendance_late_ids(self):
        for rec in self:
            rec.attendance_late_ids = False
            if rec.employee_id and rec.date_from and rec.date_to:
                attendance_ids = rec.env['hr.attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('late', '>', 0)])
                if attendance_ids:
                    attendance_late_ids = attendance_ids.filtered(
                        lambda x: x.check_in.date() >= rec.date_from
                                  and (x.check_out.date() <= rec.date_to) if x.check_out else False
                    )
                    xl = [Command.set(attendance_late_ids.ids)]
                    rec.attendance_late_ids = [Command.set(attendance_late_ids.ids)]

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_attendance_early_ids(self):
        for rec in self:
            rec.attendance_early_ids = False
            if rec.employee_id and rec.date_from and rec.date_to:
                attendance_ids = rec.env['hr.attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('early', '>', 0)])
                if attendance_ids:
                    attendance_early_ids = attendance_ids.filtered(
                        lambda x: x.check_in.date() >= rec.date_from
                                  and (x.check_out.date() <= rec.date_to) if x.check_out else False
                    )
                    rec.attendance_early_ids = [
                        Command.set(attendance_early_ids.ids)]

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_attendance_leave_ids(self):
        for rec in self:
            rec.attendance_leave_ids = False
            if rec.employee_id and rec.date_from and rec.date_to:
                attendance_ids = rec.env['hr.attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('leave_before_time', '>', 0)])
                if attendance_ids:
                    attendance_leave = attendance_ids.filtered(
                        lambda x: x.check_in.date() >= rec.date_from
                                  and (x.check_out.date() <= rec.date_to) if x.check_out else False
                    )
                    rec.attendance_leave_ids = [
                        Command.set(attendance_leave.ids)]

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_attendance_extra_hours_ids(self):
        for rec in self:
            rec.attendance_extra_hours_ids = False
            if rec.employee_id and rec.date_from and rec.date_to:
                attendance_ids = rec.env['hr.attendance'].search(
                    [('employee_id', '=', rec.employee_id.id), ('extra_hours', '>', 0)])
                if attendance_ids:
                    attendance_extra_hours_ids = attendance_ids.filtered(
                        lambda x: x.check_in.date() >= rec.date_from
                                  and (x.check_out.date() <= rec.date_to) if x.check_out else False
                    )
                    rec.attendance_extra_hours_ids = [
                        Command.set(attendance_extra_hours_ids.ids)]

    @api.depends('attendance_late_ids')
    def _compute_total_attendance_late(self):
        for rec in self:
            if rec.employee_id and rec.attendance_late_ids:
                rec.total_attendance_late = sum(rec.attendance_late_ids.mapped('late'))
                late_hour_cost = self.domain_append_hours_late()
                rec.total_attendance_cost = late_hour_cost
            else:
                rec.total_attendance_late = 0
                rec.total_attendance_cost = 0
                return True

    def domain_append_hours_late(self):
        for rec in self:
            cost = []
            first_late = self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_first_time')
            first_time = self.GetFloatOvertime(float(first_late))
            second_late = self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_second_time')
            second_time = self.GetFloatOvertime(float(second_late))
            third_late = self.env['ir.config_parameter'].get_param(
                'zakariahone_attendance.late_third_time')
            third_time = self.GetFloatOvertime(float(third_late))

    @api.depends('attendance_leave_ids')
    def _compute_total_attendance_leave(self):
        for rec in self:
            if rec.employee_id and rec.attendance_leave_ids:
                rec.total_leave_hours_payslip = sum(rec.attendance_leave_ids.mapped('leave_before_time'))
                leave_hour = self.env['ir.config_parameter'].get_param(
                    'zakariahone_attendance.before_time_leave')
                leave_hour_cost = self.env['ir.config_parameter'].get_param(
                    'zakariahone_attendance.before_time_leave_cost')
                final_hours = rec.total_leave_hours_payslip / float(leave_hour)
                rec.total_leave_hour_cost = final_hours * float(leave_hour_cost)
            else:
                rec.total_leave_hours_payslip = 0
                rec.total_leave_hour_cost = 0
                return True

    @api.depends('attendance_early_ids')
    def _compute_total_attendance_early(self):
        for rec in self:
            rec.total_attendance_early = sum(
                rec.attendance_early_ids.mapped('early'))

    @api.depends('attendance_extra_hours_ids')
    def _compute_total_extra_hours(self):
        for rec in self:
            if rec.employee_id:
                param = self.env['ir.config_parameter'].get_param(
                    'zakariahone_attendance.overtime_rate')
                overtime = float(param)
                rec.total_extra_hours = sum(
                    rec.attendance_extra_hours_ids.mapped('extra_hours')) * overtime
            else:
                rec.total_extra_hours = 0

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_number_hours_per_month(self):
        for rec in self:
            rec.number_hours_per_month = 0.0
            if rec.employee_id and rec.date_from and rec.date_to:
                date_start = rec.date_from

                week_days = dict(self.env['resource.calendar.attendance'].with_context(lang='en_US').fields_get(
                    'dayofweek')['dayofweek']['selection'])

                week_days = dict([(value, key) for key, value in week_days.items()])
                resource_calendar = rec.employee_id.resource_calendar_id

                days = resource_calendar.attendance_ids

                while date_start <= rec.date_to:
                    day = date_start.strftime('%A')
                    week_day = week_days[day]
                    get_days = days.filtered(lambda d: d.dayofweek == week_day)
                    if get_days:
                        rec.number_hours_per_month += rec.employee_id.resource_calendar_id.hours_per_day
                    date_start += timedelta(days=1)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_number_days_per_month(self):
        for rec in self:
            rec.number_days_per_month = 0.0
            if rec.employee_id and rec.date_from and rec.date_to:
                date_start = rec.date_from

                week_days = dict(self.env['resource.calendar.attendance'].with_context(lang='en_US').fields_get(
                    'dayofweek')['dayofweek']['selection'])

                week_days = dict([(value, key) for key, value in week_days.items()])
                resource_calendar = rec.employee_id.resource_calendar_id

                days = resource_calendar.attendance_ids

                while date_start <= rec.date_to:
                    day = date_start.strftime('%A')
                    week_day = week_days[day]
                    get_days = days.filtered(lambda d: d.dayofweek == week_day)
                    if get_days:
                        rec.number_days_per_month += 1
                    date_start += timedelta(days=1)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_total_absence_per_month(self):
        for rec in self:
            rec.total_absence_per_month = 0
            start = time(0, 0)
            end = time(23, 59)

            date_from = datetime.combine(rec.date_from, start)
            date_to = datetime.combine(rec.date_to, end)
            employee_monthly_attendance = rec.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', date_from),
                ('check_out', '<=', date_to)
            ])
            if rec.employee_id and rec.date_from and rec.date_to:
                date_start = rec.date_from
                week_days = dict(
                    self.env['resource.calendar.attendance'].with_context(lang='en_US').fields_get('dayofweek')[
                        'dayofweek']['selection'])
                week_days = dict([(value, key) for key, value in week_days.items()])

                resource_calendar = rec.employee_id.resource_calendar_id

                days = resource_calendar.attendance_ids
                while date_start <= rec.date_to:
                    day = date_start.strftime('%A')
                    week_day = week_days[day]
                    get_days = days.filtered(lambda d: d.dayofweek == week_day)
                    if get_days:
                        presence = employee_monthly_attendance.filtered(lambda x: x.check_in.date() == date_start)
                        if not presence:
                            print('date_start', date_start)
                            rec.total_absence_per_month += 1
                    date_start += timedelta(days=1)


class LateLimit(models.TransientModel):
    _inherit = 'res.config.settings'

    late_first_time = fields.Float(
        string='Absent For First Time',
        config_parameter='zakariahone_attendance.late_first_time'
    )
    late_first_cost = fields.Float(
        string='Absent For First  Cost',
        config_parameter='zakariahone_attendance.late_first_cost'
    )

    late_second_time = fields.Float(
        string='Absent For First Time',
        config_parameter='zakariahone_attendance.late_second_time'
    )
    late_second_cost = fields.Float(
        string='Absent For First  Cost',
        config_parameter='zakariahone_attendance.late_second_cost'
    )
    late_third_time = fields.Float(
        string='Late For First Time',
        config_parameter='zakariahone_attendance.late_third_time'
    )
    late_third_cost = fields.Float(
        string='Late For First Cost',
        config_parameter='zakariahone_attendance.late_third_cost'
    )

    before_time_leave = fields.Float(
        string='leave before time',
        config_parameter='zakariahone_attendance.before_time_leave'
    )
    before_time_leave_cost = fields.Float(
        string='leave before cost',
        config_parameter='zakariahone_attendance.before_time_leave_cost'
    )

    overtime_rate = fields.Float(
        string='Overtime Hour Rate',
        config_parameter='zakariahone_attendance.overtime_rate')

    late_hours_rate = fields.Float(
        string='Late Hour Rate',
        config_parameter='zakariahone_attendance.late_hours_rate'
    )
    absent1 = fields.Float(
        string='Late Hour Rate',
        config_parameter='zakariahone_attendance.absent1'
    )
    absent2 = fields.Float(
        string='Late Hour Rate',
        config_parameter='zakariahone_attendance.absent2'
    )
    absent3 = fields.Float(
        string='Late Hour Rate',
        config_parameter='zakariahone_attendance.absent3'
    )
