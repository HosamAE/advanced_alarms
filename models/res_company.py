# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    advanced_alarm_sound_id = fields.Many2one('advanced.alarm.sound', string='Default Alarm Sound', domain="[('sound_type', '=', 'alarm')]")
    advanced_timer_sound_id = fields.Many2one('advanced.alarm.sound', string='Default Timer Sound', domain="[('sound_type', '=', 'timer')]")
    advanced_notif_sound_id = fields.Many2one('advanced.alarm.sound', string='Default Notification Sound', domain="[('sound_type', '=', 'notif')]")
