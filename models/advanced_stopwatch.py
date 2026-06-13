# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class AdvancedStopwatch(models.Model):
    _name = 'advanced.stopwatch'
    _description = 'Time Management - Stopwatch'
    _order = 'id desc'

    name = fields.Char(string='Label', default='Stopwatch')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, index=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('running', 'Running'),
        ('paused', 'Paused')
    ], string='State', default='draft', required=True)
    
    start_time = fields.Datetime(string='Start Time')
    paused_time = fields.Datetime(string='Paused Time')
    accumulated_paused = fields.Integer(string='Accumulated Paused (Seconds)', default=0)
    split_times = fields.Text(string='Splits/Laps', help='JSON array of split times (Legacy)')
    
    lap_ids = fields.One2many('advanced.stopwatch.lap', 'stopwatch_id', string='Laps')
    display_timer = fields.Char(string='Timer', compute='_compute_display_timer')

    alert_interval = fields.Integer(string='Alert Every (Seconds)', default=60, help='Notify the user periodically while running')
    show_in_systray = fields.Boolean(string="Show in Systray", default=True, help="If checked, this stopwatch will appear in the top bar menu.")

    def _compute_display_timer(self):
        for record in self:
            record.display_timer = "00:00:00"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AdvancedStopwatch, self).create(vals_list)
        for record in records:
            record._send_bus_notification('create')
        return records

    def write(self, vals):
        res = super(AdvancedStopwatch, self).write(vals)
        if any(f in vals for f in ['state', 'split_times', 'name', 'alert_interval']):
            for record in self:
                record._send_bus_notification('write')
        return res

    def action_start(self):
        for record in self:
            if record.state in ['draft', 'paused']:
                if record.state == 'draft':
                    record.write({
                        'state': 'running',
                        'start_time': fields.Datetime.now(),
                    })
                else:
                    # Adjust accumulated paused time
                    delta = (fields.Datetime.now() - record.paused_time).total_seconds()
                    record.write({
                        'state': 'running',
                        'accumulated_paused': record.accumulated_paused + int(delta),
                        'paused_time': False,
                    })
                record._send_bus_notification('start')

    def action_pause(self):
        for record in self:
            if record.state == 'running':
                record.write({
                    'state': 'paused',
                    'paused_time': fields.Datetime.now()
                })
                record._send_bus_notification('pause')

    def action_reset(self):
        for record in self:
            record.write({
                'state': 'draft',
                'start_time': False,
                'paused_time': False,
                'accumulated_paused': 0,
                'split_times': False
            })
            record.lap_ids.unlink()
            record._send_bus_notification('reset')

    def action_lap(self):
        for record in self:
            if record.state != 'running':
                continue
            now = fields.Datetime.now()
            delta = (now - record.start_time).total_seconds() - record.accumulated_paused
            try:
                splits = json.loads(record.split_times or '[]')
            except (ValueError, TypeError):
                splits = []
            prev_split = float(splits[-1]) if splits else 0
            diff = delta - prev_split
            record.action_add_lap(delta, diff)
            record._send_bus_notification('lap')

    def action_add_lap(self, lap_seconds, diff_seconds):
        self.ensure_one()
        
        # Formatting seconds to HH:MM:SS
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        next_lap = len(self.lap_ids) + 1
        self.env['advanced.stopwatch.lap'].create({
            'stopwatch_id': self.id,
            'lap_number': next_lap,
            'lap_time_str': format_time(lap_seconds),
            'diff_time_str': format_time(diff_seconds),
            'sequence': next_lap * 10
        })
        
        # Keep legacy JSON updated for systray (or update JS later to use lap_ids)
        try:
            splits = json.loads(self.split_times or '[]')
        except (ValueError, TypeError):
            splits = []
        splits.append(lap_seconds)
        self.split_times = json.dumps(splits)

    def _send_bus_notification(self, action_type):
        self.ensure_one()
        bus_channel = f"advanced_alarms_{self.user_id.id}"
        payload = {
            'type': 'stopwatch_update',
            'id': self.id,
            'action': action_type,
            'state': self.state,
            'name': self.name,
            'accumulated_paused': self.accumulated_paused,
            'start_time': fields.Datetime.to_string(self.start_time) if self.start_time else False,
            'paused_time': fields.Datetime.to_string(self.paused_time) if self.paused_time else False,
            'split_times': self.split_times or '[]',
            'alert_interval': self.alert_interval,
            'show_in_systray': self.show_in_systray,
        }
        self.env['bus.bus']._sendone(bus_channel, 'advanced_alarms/update', payload)

    @api.model
    def get_active_stopwatches(self):
        stopwatches = self.search([
            ('user_id', '=', self.env.user.id),
            ('state', 'in', ['draft', 'running', 'paused']),
            ('show_in_systray', '=', True)
        ])
        result = []
        for sw in stopwatches:
            result.append({
                'id': sw.id,
                'name': sw.name,
                'state': sw.state,
                'accumulated_paused': sw.accumulated_paused,
                'start_time': fields.Datetime.to_string(sw.start_time) if sw.start_time else False,
                'paused_time': fields.Datetime.to_string(sw.paused_time) if sw.paused_time else False,
                'split_times': sw.split_times or '[]',
                'alert_interval': sw.alert_interval,
            })
        return result

