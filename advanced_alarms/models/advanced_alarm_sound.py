# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdvancedAlarmSound(models.Model):
    _name = 'advanced.alarm.sound'
    _description = 'Alarm & Timer Sounds'

    name = fields.Char(string='Sound Name', required=True)
    sound_type = fields.Selection([
        ('alarm', 'Alarm Sound'),
        ('timer', 'Timer Sound'),
        ('notif', 'Notification Sound')
    ], string='Type', default='alarm', required=True)
    
    file = fields.Binary(string='Audio File', attachment=True, help='Upload an MP3 or OGG file (Non-musical sounds recommended)')
    file_name = fields.Char(string='File Name')
    is_default = fields.Boolean(string='Default Sound', default=False)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user, index=True, help='Owner of this custom sound. If blank, it is a global sound.')

    @api.model
    def init_default_sounds(self):
        """Method to initialize default non-musical sounds if not present."""
        # This will be populated with Odoo data files or base64 files.
        # For now, we will add placeholders in code or XML data.
        pass

