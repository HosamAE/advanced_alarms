# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    alarm_sound_id = fields.Many2one('advanced.alarm.sound', string='Default Alarm Sound', domain="[('sound_type', '=', 'alarm')]")
    timer_sound_id = fields.Many2one('advanced.alarm.sound', string='Default Timer Sound', domain="[('sound_type', '=', 'timer')]")
    pinned_clock_ids = fields.Many2many('advanced.world.clock', string='Pinned Clocks')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'alarm_sound_id', 'timer_sound_id', 'pinned_clock_ids'
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'alarm_sound_id', 'timer_sound_id', 'pinned_clock_ids'
        ]
