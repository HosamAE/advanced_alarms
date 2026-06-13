# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime


class TestAdvancedAlarms(TransactionCase):

    def setUp(self):
        super(TestAdvancedAlarms, self).setUp()
        self.Alarm = self.env['advanced.alarm']
        self.user = self.env.user

    def test_cycle_length_constraint(self):
        """Test that cycle_days_count cannot exceed 60."""
        with self.assertRaises(ValidationError): # type: ignore
            self.Alarm.create({
                'name': 'Test Alarm',
                'user_id': self.user.id,
                'alarm_time': datetime.now(),
                'recurrence_type': 'cycle',
                'cycle_days_count': 65
            })

    def test_cycle_lines_generation(self):
        """Test that cycle lines are properly generated/cleared."""
        alarm = self.Alarm.create({
            'name': 'Test Cycle',
            'user_id': self.user.id,
            'alarm_time': datetime.now(),
            'recurrence_type': 'cycle',
            'cycle_days_count': 5
        })
        # Simulate onchange behavior
        alarm._onchange_cycle_days_count()
        self.assertEqual(len(alarm.cycle_day_ids), 5, "Should generate exactly 5 cycle lines.")
        
        # Change type to once, lines should clear
        alarm.recurrence_type = 'once'
        alarm._onchange_cycle_days_count()
        self.assertEqual(len(alarm.cycle_day_ids), 0, "Should clear cycle lines when type is not cycle.")

    def test_timer_duration_conversion(self):
        """Test that hours, minutes, seconds correctly compute the total duration and vice versa."""
        Timer = self.env['advanced.timer']
        timer = Timer.create({
            'name': 'Test Timer',
            'user_id': self.user.id,
            'duration': 3665 # 1 hour, 1 minute, 5 seconds
        })
        self.assertEqual(timer.duration_hours, 1)
        self.assertEqual(timer.duration_minutes, 1)
        self.assertEqual(timer.duration_seconds, 5)

        # Update via parts
        timer.write({
            'duration_hours': 2,
            'duration_minutes': 30,
            'duration_seconds': 15
        })
        self.assertEqual(timer.duration, 9015) # (2*3600) + (30*60) + 15

    def test_alarm_states_and_cleanup(self):
        """Test alarm mute, done, and clear muted logic."""
        alarm = self.Alarm.create({
            'name': 'State Test',
            'user_id': self.user.id,
            'alarm_time': datetime.now(),
        })
        self.assertEqual(alarm.state, 'pending')
        
        # Test Mute
        alarm.action_mute()
        self.assertEqual(alarm.state, 'muted')
        
        # Test Done
        alarm.state = 'pending'
        alarm.action_done()
        self.assertEqual(alarm.state, 'done')
        
        # Test Clear Muted
        self.Alarm.action_clear_muted_alarms()
        self.assertFalse(alarm.exists(), "Alarm should be deleted after clearing muted/done alarms.")

    def test_stopwatch_states(self):
        """Test stopwatch start, pause, reset, and lap logic."""
        Stopwatch = self.env['advanced.stopwatch']
        sw = Stopwatch.create({
            'name': 'Test SW',
            'user_id': self.user.id,
        })
        self.assertEqual(sw.state, 'draft')
        
        # Start
        sw.action_start()
        self.assertEqual(sw.state, 'running')
        self.assertTrue(sw.start_time)
        
        # Lap
        sw.action_add_lap(10.5, 10.5)
        self.assertIn("10.5", sw.split_times)
        
        # Pause
        sw.action_pause()
        self.assertEqual(sw.state, 'paused')
        self.assertTrue(sw.paused_time)
        
        # Reset
        sw.action_reset()
        self.assertEqual(sw.state, 'draft')
        self.assertFalse(sw.start_time)
        self.assertFalse(sw.paused_time)
