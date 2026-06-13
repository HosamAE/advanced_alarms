# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AdvancedAlarm(models.Model):
    _name = 'advanced.alarm'
    _description = 'Advanced Alarm'
    _order = 'alarm_time asc, is_critical desc, id desc'

    name = fields.Char(string='Alarm Title', required=True)
    user_id = fields.Many2one('res.users', string='Assigned User', default=lambda self: self.env.user, index=True)
    group_ids = fields.Many2many('res.groups', string='Target Groups', help='If selected, this alarm will be visible to all members of these groups.')
    alarm_time = fields.Datetime(string='Alarm Time', required=True, index=True, default=fields.Datetime.now)
    message = fields.Text(string='Message')
    is_critical = fields.Boolean(string='Critical Alarm', default=False)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('pre_alarm', 'Pre-Alarm Sent'),
        ('active', 'Ringing'),
        ('done', 'Done'),
        ('muted', 'Muted'),
        ('cancel', 'Cancelled')
    ], string='Status', default='pending', required=True, index=True)
    
    def _default_sound_id(self):
        user_sound = self.env.user.alarm_sound_id
        if user_sound:
            return user_sound.id
        return self.env.company.advanced_alarm_sound_id.id

    sound_id = fields.Many2one('advanced.alarm.sound', string='Ringtone', default=_default_sound_id, domain="[('sound_type', '=', 'alarm')]")
    
    pre_alarm = fields.Boolean(string='Enable Pre-alarm', default=True)
    pre_alarm_duration = fields.Integer(string='Pre-alarm Time (Minutes)', default=5)
    
    # Recurrence Fields
    recurrence_type = fields.Selection([
        ('once', 'Once'),
        ('cycle', 'Cycle'),
        ('scrum', 'Scramble!'),
        ('shift', 'Shifts'),
        ('custom', 'Custom')
    ], string='Repeat', default='once', required=True)
    
    recur_mon = fields.Boolean(string='Monday', default=False)
    recur_tue = fields.Boolean(string='Tuesday', default=False)
    recur_wed = fields.Boolean(string='Wednesday', default=False)
    recur_thu = fields.Boolean(string='Thursday', default=False)
    recur_fri = fields.Boolean(string='Friday', default=False)
    recur_sat = fields.Boolean(string='Saturday', default=False)
    recur_sun = fields.Boolean(string='Sunday', default=False)
    
    # Shift Schedule Fields
    shift_work_days = fields.Integer(string='Work Days (Shifts)', default=3)
    shift_off_days = fields.Integer(string='Off Days', default=4)
    shift_start_date = fields.Date(string='Shift Cycle Start Date', default=fields.Date.context_today)
    
    # 30-Day Cycle Fields
    cycle_start_date = fields.Date(string='Cycle Start Date', default=fields.Date.context_today)
    cycle_days_count = fields.Integer(string='Cycle Length (Days)', default=7)
    cycle_day_ids = fields.One2many('advanced.alarm.cycle.day', 'alarm_id', string='Cycle Days')
    
    @api.constrains('cycle_days_count')
    def _check_cycle_days_count(self):
        for record in self:
            if record.recurrence_type == 'cycle' and (record.cycle_days_count < 1 or record.cycle_days_count > 60):
                raise ValidationError(self.env._("Cycle Length must be between 1 and 60 days."))
                
    @api.onchange('recurrence_type', 'cycle_days_count')
    def _onchange_cycle_days_count(self):
        if self.recurrence_type != 'cycle':
            self.cycle_day_ids = [(5, 0, 0)]
            return
            
        if self.cycle_days_count < 1 or self.cycle_days_count > 60:
            return
            
        current_lines = self.cycle_day_ids
        current_count = len(current_lines)
        target_count = self.cycle_days_count
        
        if current_count < target_count:
            # Need to add lines
            commands = []
            for i in range(current_count + 1, target_count + 1):
                commands.append((0, 0, {
                    'day_index': i,
                    'is_active': False,
                    'alarm_time': 8.0
                }))
            self.cycle_day_ids = commands
        elif current_count > target_count:
            # Need to remove lines
            lines_to_keep = current_lines.sorted('day_index')[:target_count]
            self.cycle_day_ids = lines_to_keep
    
    # Intraday Fields (Repeat during the day)
    intraday_repeat = fields.Boolean(string='Repeat During the Day', default=False)
    intraday_interval = fields.Integer(string='Interval', default=4)
    intraday_uom = fields.Selection([
        ('hours', 'Hours'),
        ('minutes', 'Minutes')
    ], string='Interval Unit', default='hours')
    
    snoozed_count = fields.Integer(string='Snoozed Count', default=0)
    
    next_run_datetime = fields.Datetime(string='Next Run', compute='_compute_next_run_datetime')
    
    @api.depends('alarm_time', 'recurrence_type', 'recur_mon', 'recur_tue', 'recur_wed', 'recur_thu', 'recur_fri', 'recur_sat', 'recur_sun', 
                 'shift_work_days', 'shift_off_days', 'shift_start_date', 'cycle_day_ids', 'cycle_day_ids.is_active', 'cycle_day_ids.alarm_time', 'intraday_repeat', 'intraday_interval', 'intraday_uom')
    def _compute_next_run_datetime(self):
        for record in self:
            try:
                # Calculate next occurrence dynamically for preview purposes
                record.next_run_datetime = record._get_next_recurrence_datetime()
            except Exception:
                record.next_run_datetime = False
    
    # Polymorphic relations to Odoo Records
    res_model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)
    res_name = fields.Char(string='Related Document Name')

    @api.constrains('pre_alarm_duration')
    def _check_pre_alarm_duration(self):
        for record in self:
            if record.pre_alarm_duration < 0:
                raise ValidationError(self.env._("Pre-alarm duration cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AdvancedAlarm, self).create(vals_list)
        for record in records:
            record._send_bus_notification('create')
        return records

    def write(self, vals):
        res = super(AdvancedAlarm, self).write(vals)
        fields_to_check = [
            'state', 'alarm_time', 'name', 'message', 'is_critical', 'snoozed_count',
            'recurrence_type', 'shift_work_days', 'shift_off_days', 'shift_start_date',
            'intraday_repeat', 'intraday_interval', 'intraday_uom',
            'ringtone_id', 'description', 'target_groups_ids', 'enable_pre_alarm', 'pre_alarm_time'
        ]
        if any(f in vals for f in fields_to_check):
            for record in self:
                record._send_bus_notification('write')
        return res

    def action_mute(self):
        for record in self:
            if record.recurrence_type != 'once':
                next_time = record._get_next_recurrence_datetime()
                record.write({
                    'alarm_time': next_time,
                    'state': 'pending',
                    'snoozed_count': 0,
                })
            else:
                record.write({'state': 'muted'})

    def action_done(self):
        for record in self:
            if record.recurrence_type != 'once':
                next_time = record._get_next_recurrence_datetime()
                record.write({
                    'alarm_time': next_time,
                    'state': 'pending',
                    'snoozed_count': 0,
                })
            else:
                record.write({'state': 'done'})

    def action_snooze(self):
        for alarm in self:
            snooze_duration = self.env['ir.config_parameter'].sudo().get_param('advanced_alarms.snooze_duration', default=10)
            alarm.alarm_time = fields.Datetime.now() + timedelta(minutes=int(snooze_duration))
            alarm.state = 'pending'
            
            # Send bus notification to update systray
            alarm._send_bus_notification('update')
            
    def action_cancel(self):
        for alarm in self:
            if alarm.state not in ['done', 'cancel']:
                alarm.state = 'cancel'
                alarm._send_bus_notification('remove')
                
    def action_draft(self):
        for alarm in self:
            if alarm.state in ['done', 'cancel', 'muted']:
                alarm.state = 'pending'
                # Optionally reset alarm_time if it's in the past? 
                # For now, just set state. User can edit time.
                alarm._send_bus_notification('update')

    def _get_next_recurrence_datetime(self):
        self.ensure_one()
        user_tz = self.user_id.tz or 'UTC'
        tz = pytz.timezone(user_tz)
        
        now_local = datetime.now(tz)
        alarm_local = pytz.utc.localize(self.alarm_time).astimezone(tz)
        
        # 1. Intraday Check for TODAY
        if self.intraday_repeat and self.intraday_interval > 0:
            interval_delta = timedelta(hours=self.intraday_interval) if self.intraday_uom == 'hours' else timedelta(minutes=self.intraday_interval)
            
            is_today_valid = False
            weekday = now_local.weekday()
            
            if self.recurrence_type == 'custom':
                day_map = {0: self.recur_mon, 1: self.recur_tue, 2: self.recur_wed, 3: self.recur_thu, 4: self.recur_fri, 5: self.recur_sat, 6: self.recur_sun}
                is_today_valid = day_map.get(weekday, False)
            elif self.recurrence_type == 'shift':
                if self.shift_start_date and self.shift_work_days > 0:
                    cycle_length = self.shift_work_days + self.shift_off_days
                    if cycle_length > 0:
                        start_date = self.shift_start_date
                        days_diff = (now_local.date() - start_date).days
                        if days_diff >= 0 and (days_diff % cycle_length) < self.shift_work_days:
                            is_today_valid = True
            elif self.recurrence_type == 'cycle':
                if self.cycle_day_ids:
                    start_date = self.shift_start_date or fields.Date.context_today(self)
                    days_diff = (now_local.date() - start_date).days
                    if days_diff >= 0:
                        cycle_length = len(self.cycle_day_ids)
                        day_index = (days_diff % cycle_length) + 1
                        cycle_day = self.cycle_day_ids.filtered(lambda d: d.day_index == day_index)
                        if cycle_day and cycle_day.is_active:
                            is_today_valid = True
                            alarm_local = alarm_local.replace(
                                hour=int(cycle_day.alarm_time),
                                minute=int((cycle_day.alarm_time % 1) * 60)
                            )
            
            if is_today_valid:
                base_time = now_local.replace(
                    hour=alarm_local.hour,
                    minute=alarm_local.minute,
                    second=alarm_local.second,
                    microsecond=0
                )
                
                if now_local < base_time:
                    return base_time.astimezone(pytz.utc).replace(tzinfo=None)
                
                next_intraday = base_time
                while next_intraday <= now_local:
                    next_intraday += interval_delta
                
                if next_intraday.date() == now_local.date():
                    return next_intraday.astimezone(pytz.utc).replace(tzinfo=None)
        
        # 2. Daily Calculation (Find the next valid day)
        start_date = max(alarm_local, now_local)
        
        for i in range(1, 100):
            next_date = start_date + timedelta(days=i)
            weekday = next_date.weekday()
            
            is_match = False
            custom_alarm_time = None
            
            if self.recurrence_type == 'scrum':
                if weekday in [0, 1, 2, 3, 6]:
                    is_match = True
            elif self.recurrence_type == 'custom':
                day_map = {0: self.recur_mon, 1: self.recur_tue, 2: self.recur_wed, 3: self.recur_thu, 4: self.recur_fri, 5: self.recur_sat, 6: self.recur_sun}
                if day_map.get(weekday, False):
                    is_match = True
            elif self.recurrence_type == 'shift':
                if self.shift_start_date and self.shift_work_days > 0:
                    cycle_length = self.shift_work_days + self.shift_off_days
                    if cycle_length > 0:
                        start_date_obj = self.shift_start_date
                        days_diff = (next_date.date() - start_date_obj).days
                        if days_diff >= 0 and (days_diff % cycle_length) < self.shift_work_days:
                            is_match = True
            elif self.recurrence_type == 'cycle':
                if self.cycle_day_ids:
                    start_date_obj = self.shift_start_date or fields.Date.context_today(self)
                    days_diff = (next_date.date() - start_date_obj).days
                    if days_diff >= 0:
                        cycle_length = len(self.cycle_day_ids)
                        day_index = (days_diff % cycle_length) + 1
                        cycle_day = self.cycle_day_ids.filtered(lambda d: d.day_index == day_index)
                        if cycle_day and cycle_day.is_active:
                            is_match = True
                            custom_alarm_time = cycle_day.alarm_time
            
            if is_match:
                if custom_alarm_time is not None:
                    h = int(custom_alarm_time)
                    m = int((custom_alarm_time % 1) * 60)
                else:
                    h = alarm_local.hour
                    m = alarm_local.minute
                    
                next_alarm_local = next_date.replace(
                    hour=h,
                    minute=m,
                    second=alarm_local.second,
                    microsecond=0
                )
                return next_alarm_local.astimezone(pytz.utc).replace(tzinfo=None)
                
        fallback_local = alarm_local + timedelta(days=1)
        return fallback_local.astimezone(pytz.utc).replace(tzinfo=None)

    def _send_bus_notification(self, action_type):
        """Send a real-time message via Odoo Bus to the user's browser."""
        self.ensure_one()
        bus_channel = f"advanced_alarms_{self.user_id.id}"
        payload = {
            'type': 'alarm_update',
            'id': self.id,
            'action': action_type,
            'name': self.name,
            'state': self.state,
            'alarm_time': fields.Datetime.to_string(self.alarm_time),
            'message': self.message or '',
            'is_critical': self.is_critical,
            'sound_src': f"/web/content/advanced.alarm.sound/{self.sound_id.id}/file" if self.sound_id else "",
            'pre_alarm': self.pre_alarm,
            'pre_alarm_duration': self.pre_alarm_duration,
            'res_model': self.res_model or '',
            'res_id': self.res_id or 0,
            'res_name': self.res_name or '',
            'recurrence_type': self.recurrence_type,
            'snoozed_count': self.snoozed_count,
            'snooze_limit_reached': self.snoozed_count >= int(self.env['ir.config_parameter'].sudo().get_param('advanced_alarms.snooze_limit', 3)),
        }
        self.env['bus.bus']._sendone(self.user_id.partner_id, 'advanced_alarms/update', payload)

    @api.model
    def get_todays_alarms(self):
        """Fetch today's alarms for the current user in their local timezone."""
        user_tz = self.env.user.tz or 'UTC'
        tz = pytz.timezone(user_tz)
        
        # Get local today start and end
        now_local = datetime.now(tz)
        local_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        local_end = now_local.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Convert to UTC for DB query
        utc_start = local_start.astimezone(pytz.utc).replace(tzinfo=None)
        utc_end = local_end.astimezone(pytz.utc).replace(tzinfo=None)
        
        alarms = self.search([
            '|', 
            ('user_id', '=', self.env.user.id),
            ('group_ids', 'in', self.env.user.group_ids.ids),
            ('alarm_time', '>=', utc_start),
            ('alarm_time', '<=', utc_end)
        ])
        
        result = []
        for alarm in alarms:
            result.append({
                'id': alarm.id,
                'name': alarm.name,
                'alarm_time': fields.Datetime.to_string(alarm.alarm_time),
                'message': alarm.message or '',
                'is_critical': alarm.is_critical,
                'state': alarm.state,
                'sound_src': f"/web/content/advanced.alarm.sound/{alarm.sound_id.id}/file" if alarm.sound_id else "",
                'pre_alarm': alarm.pre_alarm,
                'pre_alarm_duration': alarm.pre_alarm_duration,
                'res_model': alarm.res_model or '',
                'res_id': alarm.res_id or 0,
                'res_name': alarm.res_name or '',
                'recurrence_type': alarm.recurrence_type,
                'snoozed_count': alarm.snoozed_count,
                'snooze_limit_reached': alarm.snoozed_count >= int(self.env['ir.config_parameter'].sudo().get_param('advanced_alarms.snooze_limit', 3)),
            })
            
        old_muted_count = self.search_count([
            ('user_id', '=', self.env.user.id),
            ('state', 'in', ['muted', 'done'])
        ])
            
        return {
            'alarms': result,
            'old_muted_count': old_muted_count
        }

    @api.model
    def cron_clean_old_alarms(self):
        """Delete old completed or muted alarms based on global retention settings."""
        from datetime import timedelta
        get_param = self.env['ir.config_parameter'].sudo().get_param
        retention_days = int(get_param('advanced_alarms.retention_period', 30))
        limit_date = fields.Datetime.now() - timedelta(days=retention_days)
        old_alarms = self.search([
            ('state', 'in', ['done', 'muted']),
            ('alarm_time', '<', limit_date)
        ])
        if old_alarms:
            old_alarms.unlink()

    @api.model
    def cron_remind_cleanup(self):
        """Notify users who have accumulated too many finished/muted alarms or inactive timers."""
        users = self.env['res.users'].search([])
        for user in users:
            done_alarms_count = self.search_count([
                ('user_id', '=', user.id),
                ('state', 'in', ['done', 'muted'])
            ])
            done_timers_count = self.env['advanced.timer'].search_count([
                ('user_id', '=', user.id),
                ('state', '=', 'done')
            ])
            
            if done_alarms_count > 10 or done_timers_count > 10:
                payload = {
                    'type': 'cleanup_reminder',
                    'message': self.env._("You have accumulated finished alarms or timers. Please clean them up to declutter your workspace.")
                }
                self.env['bus.bus']._sendone(user.partner_id, 'advanced_alarms/update', payload)

    @api.model
    def action_clear_muted_alarms(self):
        """Action for users to manually clear their own muted alarms."""
        muted_alarms = self.search([
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'muted')
        ])
        count = len(muted_alarms)
        muted_alarms.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cleanup Successful',
                'message': f'Removed {count} muted alarms.',
                'type': 'success',
                'sticky': False,
            }
        }
        
    @api.model
    def _cron_auto_cleanup(self):
        """Cron job to automatically clean up old alarms based on settings."""
        retention_days = int(self.env['ir.config_parameter'].sudo().get_param('advanced_alarms.retention_period', default=30))
        cutoff_date = fields.Datetime.now() - timedelta(days=retention_days)
        
        # Find alarms that are done, muted, or cancelled and older than retention period
        old_alarms = self.search([
            ('state', 'in', ['done', 'muted', 'cancel']),
            ('alarm_time', '<', cutoff_date)
        ])
        
        if old_alarms:
            old_alarms.unlink()
            
        # Also clean up completed timers
        old_timers = self.env['advanced.timer'].search([
            ('state', 'in', ['done', 'cancel']),
            ('write_date', '<', cutoff_date)
        ])
        if old_timers:
            old_timers.unlink()

    @api.model
    def create_alarm_from_code(self, name, alarm_time, user_ids, message="", is_critical=False, res_model=False, res_id=False):
        """Method for developers to programmatically create alarms for users."""
        alarms = self.env['advanced.alarm']
        if not user_ids:
            return alarms
        
        # Resolve record name if res_model and res_id are provided
        res_name = False
        if isinstance(res_model, str) and res_id:
            record = self.env[res_model].browse(res_id)
            if record.exists():
                res_name = record.display_name

        for user in self.env['res.users'].browse(user_ids):
            alarms |= self.create({
                'name': name,
                'alarm_time': alarm_time,
                'user_id': user.id,
                'message': message,
                'is_critical': is_critical,
                'res_model': res_model,
                'res_id': res_id,
                'res_name': res_name
            })
        return alarms

    @api.model
    def get_time_management_settings(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        company = self.env.company
        timer_sound_src = f"/web/content/advanced.alarm.sound/{company.advanced_timer_sound_id.id}/file" if company.advanced_timer_sound_id else ""
        notif_sound_src = f"/web/content/advanced.alarm.sound/{company.advanced_notif_sound_id.id}/file" if company.advanced_notif_sound_id else ""
        
        return {
            'alarm_ring_duration': int(get_param('advanced_alarms.alarm_ring_duration', 60)),
            'timer_ring_repeat': int(get_param('advanced_alarms.timer_ring_repeat', 3)),
            'pre_alarm_duration': int(get_param('advanced_alarms.pre_alarm_duration', 5)),
            'notif_dismiss_duration': int(get_param('advanced_alarms.notif_dismiss_duration', 5)),
            'notif_position': get_param('advanced_alarms.notif_position', 'auto'),
            'snooze_duration': int(get_param('advanced_alarms.snooze_duration', 5)),
            'snooze_limit': int(get_param('advanced_alarms.snooze_limit', 3)),
            'stopwatch_alert_interval': int(get_param('advanced_alarms.stopwatch_alert_interval', 3600)),
            'timer_sound_src': timer_sound_src,
            'notif_sound_src': notif_sound_src,
            'is_alarm_manager': self.env.user.has_group('advanced_alarms.group_alarm_manager'),
        }

    @api.model
    def get_world_clocks(self):
        """Fetch all world clocks and annotate them with the user's pinned status."""
        clocks = self.env['advanced.world.clock'].search([])
        pinned_ids = self.env.user.pinned_clock_ids.ids
        
        result = []
        for clock in clocks:
            # Pinned if explicitly pinned by user, or if pinned by default
            is_pinned = (clock.id in pinned_ids) or clock.is_pinned_by_default
            
            result.append({
                'id': clock.id,
                'name': clock.name,
                'tz': clock.timezone,
                'dst_mode': clock.dst_mode,
                'is_pinned': is_pinned
            })
        return result

    @api.model
    def toggle_pinned_clock(self, clock_id):
        """Toggle the pinned status of a clock for the current user."""
        user = self.env.user
        if clock_id in user.pinned_clock_ids.ids:
            user.pinned_clock_ids = [(3, clock_id)]
            return False
        else:
            user.pinned_clock_ids = [(4, clock_id)]
            return True
