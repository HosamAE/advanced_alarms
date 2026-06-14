# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
from odoo import models, fields, api
import pytz


class AdvancedWorldClock(models.Model):
    _name = 'advanced.world.clock'
    _description = 'World Clock'
    _order = 'sequence, id'

    name = fields.Char(string='City / Name', required=True, translate=True)
    timezone = fields.Selection(
        selection=lambda self: [(tz, tz) for tz in pytz.all_timezones],
        string='Timezone',
        required=True,
        default='UTC'
    )
    dst_mode = fields.Selection([
        ('auto', 'Auto (Global System)'),
        ('force_add', 'Force +1 Hour (DST)'),
        ('force_sub', 'Force -1 Hour')
    ], string='DST Mode', default='auto', required=True)
    
    time_format = fields.Selection([
        ('12h', '12 Hours (AM/PM)'),
        ('24h', '24 Hours')
    ], string='Time Format', default='12h', required=True)
    
    theme_color = fields.Selection([
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
        ('primary', 'Primary Color'),
    ], string='Theme Color', default='dark')
    
    is_pinned_by_default = fields.Boolean(
        string='Pinned by Default', 
        default=False,
        help="If checked, this clock will be floating on the screen by default for all users unless they unpin it."
    )
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
