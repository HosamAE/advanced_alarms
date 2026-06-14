# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alarm_ring_duration = fields.Integer(string='Default Alarm Ring Duration (Seconds)', default=60, config_parameter='advanced_alarms.alarm_ring_duration')
    timer_ring_repeat = fields.Integer(string='Default Timer Ring Repeat Count', default=3, config_parameter='advanced_alarms.timer_ring_repeat')
    pre_alarm_duration = fields.Integer(string='Default Pre-alarm Duration (Minutes)', default=5, config_parameter='advanced_alarms.pre_alarm_duration')
    retention_period = fields.Integer(string='Alarms Retention Period (Days)', default=30, help="Days to keep completed or muted alarms before cleaning them up.", config_parameter='advanced_alarms.retention_period')
    
    notif_dismiss_duration = fields.Integer(string='Default Notification Dismiss Duration (Seconds)', default=5, config_parameter='advanced_alarms.notif_dismiss_duration')
    notif_position = fields.Selection([
        ('auto', 'Auto (RTL/LTR)'),
        ('bottom_right', 'Bottom Right'),
        ('bottom_left', 'Bottom Left'),
        ('top_right', 'Top Right'),
        ('top_left', 'Top Left')
    ], string='Default Notification Position', default='auto', config_parameter='advanced_alarms.notif_position')
    
    snooze_duration = fields.Integer(string='Default Snooze Duration (Minutes)', default=5, config_parameter='advanced_alarms.snooze_duration')
    snooze_limit = fields.Integer(string='Default Snooze Limit (Times)', default=3, config_parameter='advanced_alarms.snooze_limit')
    stopwatch_alert_interval = fields.Integer(string='Default Stopwatch Alert Interval (Seconds)', default=3600, config_parameter='advanced_alarms.stopwatch_alert_interval')

    advanced_alarm_sound_id = fields.Many2one('advanced.alarm.sound', related='company_id.advanced_alarm_sound_id', readonly=False)
    advanced_timer_sound_id = fields.Many2one('advanced.alarm.sound', related='company_id.advanced_timer_sound_id', readonly=False)
    advanced_notif_sound_id = fields.Many2one('advanced.alarm.sound', related='company_id.advanced_notif_sound_id', readonly=False)
