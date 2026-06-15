# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
import os
import base64
from datetime import datetime, timedelta
from odoo.modules.module import get_module_path


def post_init_hook(env):
    """Seed default sounds, 5 alarms, and 5 timers from filesystem/code into the database."""
    module_path = get_module_path('advanced_alarms')
    if not module_path:
        return
        
    audio_dir = os.path.join(module_path, 'static', 'src', 'audio')
    if not os.path.isdir(audio_dir):
        return
        
    sounds_to_create = [
        ('alarm_gentle_wake.wav', 'Gentle Wake (20s)', 'alarm'),
        ('alarm_modern_chime.wav', 'Modern Chime (20s)', 'alarm'),
        ('alarm_digital_clock.wav', 'Soft Digital Clock (20s)', 'alarm'),
        ('alarm_smooth_pulse.wav', 'Smooth Pulse (20s)', 'alarm'),
        ('alarm_echo_ping.wav', 'Echo Ping (20s)', 'alarm'),
        ('timer_done_chime.wav', 'Done Chime (3s)', 'timer'),
        ('timer_sharp_beep.wav', 'Sharp Beep (3s)', 'timer'),
        ('timer_alert.wav', 'Timer Alert (3s)', 'timer'),
        ('notif_pop.wav', 'Pop (1s)', 'notif'),
        ('notif_bubble.wav', 'Bubble (1s)', 'notif'),
    ]
    
    sound_obj = env['advanced.alarm.sound']
    for file_name, display_name, sound_type in sounds_to_create:
        file_path = os.path.join(audio_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = base64.b64encode(f.read())
                existing = sound_obj.search([('name', '=', display_name), ('sound_type', '=', sound_type)], limit=1)
                if not existing:
                    sound_obj.create({
                        'name': display_name,
                        'sound_type': sound_type,
                        'file': data,
                        'file_name': file_name,
                        'is_default': True,
                        'user_id': False  # Global sound
                    })

    # Seed 5 Alarms for today
    alarm_obj = env['advanced.alarm']
    now = datetime.now()
    alarms_data = [
        ('Meeting with Team', now + timedelta(minutes=5), 'Discuss project updates', False),
        ('Client Review Meeting', now + timedelta(minutes=30), 'Important review - critical alert', True),
        ('Take a Break', now + timedelta(hours=2), 'Get up and stretch', False),
        ('Daily Standup (Past)', now - timedelta(hours=1), 'Morning status update', False),
        ('Check emails (Past)', now - timedelta(hours=3), 'Inbox zero routine', False),
    ]
    
    for name, alarm_time, msg, critical in alarms_data:
        existing = alarm_obj.search([('name', '=', name), ('user_id', '=', env.uid)], limit=1)
        if not existing:
            state = 'pending'
            if alarm_time < now:
                state = 'muted'
            alarm_obj.create({
                'name': name,
                'alarm_time': alarm_time,
                'message': msg,
                'is_critical': critical,
                'state': state,
                'user_id': env.uid,
            })

    # Seed 5 Timers
    timer_obj = env['advanced.timer']
    timers_data = [
        ('Quick Coffee Break', 60),
        ('Focus Timer (Pomodoro)', 1500),
        ('Daily Standup Timer', 900),
        ('Stretch & Walk', 300),
        ('Review Checklist', 600),
    ]
    for name, duration in timers_data:
        existing = timer_obj.search([('name', '=', name), ('user_id', '=', env.uid)], limit=1)
        if not existing:
            timer_obj.create({
                'name': name,
                'duration': duration,
                'user_id': env.uid,
                'state': 'draft',
            })

