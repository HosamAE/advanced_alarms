# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields


class AdvancedStopwatchLap(models.Model):
    _name = 'advanced.stopwatch.lap'
    _description = 'Time Management - Stopwatch Lap'
    _order = 'sequence, id'

    stopwatch_id = fields.Many2one('advanced.stopwatch', string='Stopwatch', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    lap_number = fields.Integer(string='Lap #')
    
    lap_time_str = fields.Char(string='Lap Time')
    diff_time_str = fields.Char(string='Split (Diff)')
