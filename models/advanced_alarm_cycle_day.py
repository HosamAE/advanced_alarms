# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdvancedAlarmCycleDay(models.Model):
    _name = 'advanced.alarm.cycle.day'
    _description = 'Alarm Cycle Day'
    _order = 'day_index asc'

    alarm_id = fields.Many2one('advanced.alarm', string='Alarm', required=True, ondelete='cascade')
    day_index = fields.Integer(string='Day Number', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    alarm_time = fields.Float(string='Alarm Time', default=8.0)
    
    date = fields.Date(string='Date', compute='_compute_date_and_day', store=True)
    day_name = fields.Char(string='Day', compute='_compute_date_and_day', store=True)

    @api.depends('alarm_id.cycle_start_date', 'day_index')
    def _compute_date_and_day(self):
        from datetime import timedelta
        for record in self:
            if record.alarm_id.cycle_start_date and record.day_index:
                target_date = record.alarm_id.cycle_start_date + timedelta(days=record.day_index - 1)
                record.date = target_date
                record.day_name = target_date.strftime('%A')
            else:
                record.date = False
                record.day_name = ''
