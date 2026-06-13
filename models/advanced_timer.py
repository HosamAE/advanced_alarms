# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdvancedTimer(models.Model):
    _name = 'advanced.timer'
    _description = 'Time Management - Timer'
    _order = 'id desc'

    name = fields.Char(string='Label', default='Timer')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, index=True)
    duration = fields.Integer(string='Duration (Total Seconds)', required=True, default=300)
    duration_hours = fields.Integer(string='Hours', compute='_compute_duration_parts', inverse='_inverse_duration_parts', store=True)
    duration_minutes = fields.Integer(string='Minutes', compute='_compute_duration_parts', inverse='_inverse_duration_parts', store=True)
    remaining_duration = fields.Integer(string='Remaining Seconds')
    state = fields.Selection([
        ('draft', 'New'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='State', default='draft', required=True)
    
    start_time = fields.Datetime(string='Start Time')
    paused_time = fields.Datetime(string='Paused Time')
    accumulated_paused = fields.Integer(string='Accumulated Paused (Seconds)', default=0)
    sound_id = fields.Many2one('advanced.alarm.sound', string='Sound')

    @api.depends('duration')
    def _compute_duration_parts(self):
        for record in self:
            record.duration_hours = record.duration // 3600
            record.duration_minutes = (record.duration % 3600) // 60

    def _inverse_duration_parts(self):
        for record in self:
            record.duration = (record.duration_hours * 3600) + (record.duration_minutes * 60)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AdvancedTimer, self).create(vals_list)
        for record in records:
            record._send_bus_notification('create')
        return records

    def write(self, vals):
        res = super(AdvancedTimer, self).write(vals)
        if any(f in vals for f in ['state', 'duration', 'name']):
            for record in self:
                record._send_bus_notification('write')
        return res

    def action_start(self):
        for record in self:
            vals: dict = {'state': 'running'}
            if not record.start_time:
                vals['start_time'] = fields.Datetime.now()
            else:
                # If resuming from pause, compute paused duration
                if record.paused_time:
                    delta = (fields.Datetime.now() - record.paused_time).total_seconds()
                    vals['accumulated_paused'] = record.accumulated_paused + int(delta)
                    vals['paused_time'] = False
            record.write(vals)
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
                'remaining_duration': record.duration
            })
            record._send_bus_notification('reset')

    def action_done(self):
        for record in self:
            record.write({
                'state': 'done',
                'remaining_duration': 0
            })
            record._send_bus_notification('done')

    def action_cancel(self):
        for record in self:
            if record.state not in ['done', 'cancel']:
                record.write({
                    'state': 'cancel'
                })
                record._send_bus_notification('remove')
                
    def action_draft(self):
        for record in self:
            if record.state in ['done', 'cancel']:
                record.write({
                    'state': 'draft',
                    'start_time': False,
                    'paused_time': False,
                    'accumulated_paused': 0
                })
                record._send_bus_notification('update')

    def _send_bus_notification(self, action_type):
        self.ensure_one()
        bus_channel = f"advanced_alarms_{self.user_id.id}"
        payload = {
            'type': 'timer_update',
            'id': self.id,
            'action': action_type,
            'state': self.state,
            'name': self.name,
            'duration': self.duration,
            'accumulated_paused': self.accumulated_paused,
            'start_time': fields.Datetime.to_string(self.start_time) if self.start_time else False,
            'paused_time': fields.Datetime.to_string(self.paused_time) if self.paused_time else False,
            'sound_src': f"/web/content/advanced.alarm.sound/{self.sound_id.id}/file" if self.sound_id else "",
        }
        self.env['bus.bus']._sendone(self.user_id.partner_id, 'advanced_alarms/update', payload)

    @api.model
    def get_active_timers(self):
        timers = self.search([
            ('user_id', '=', self.env.user.id),
            ('state', 'in', ['draft', 'running', 'paused'])
        ])
        result = []
        for timer in timers:
            result.append({
                'id': timer.id,
                'name': timer.name,
                'state': timer.state,
                'duration': timer.duration,
                'accumulated_paused': timer.accumulated_paused,
                'start_time': fields.Datetime.to_string(timer.start_time) if timer.start_time else False,
                'paused_time': fields.Datetime.to_string(timer.paused_time) if timer.paused_time else False,
                'sound_src': f"/web/content/advanced.alarm.sound/{timer.sound_id.id}/file" if timer.sound_id else "",
            })
        return result

