# Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
# Email   : HossamA.Eissa@gmail.com
# LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
#
# This file is part of "Advanced Alarms & Time Management" for Odoo 17.
# Licensed under the Custom Attribution License — see LICENSE file for details.
# Free to use and modify; NOT allowed to re-publish under a different author name.
# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tests.common import TransactionCase


class TestAlarmRecurrence(TransactionCase):

    def setUp(self):
        super(TestAlarmRecurrence, self).setUp()
        self.user = self.env['res.users'].create({
            'name': 'Test Alarm User',
            'login': 'test_alarm_user_unique',
            'email': 'test_alarm@example.com',
            'tz': 'Europe/London',
        })
        self.Alarm = self.env['advanced.alarm'].with_user(self.user)

    def test_cycle_recurrence(self):
        # June 11, 2026 is a Thursday
        alarm_time = datetime(2026, 6, 11, 10, 0, 0)
        alarm = self.Alarm.create({
            'name': 'Weekday Alarm',
            'alarm_time': alarm_time,
            'recurrence_type': 'cycle',
            'user_id': self.user.id,
        })
        
        next_time = alarm._get_next_recurrence_datetime()
        # Next weekday recurrence from Thursday should be Friday (June 12, 2026, weekday index 4)
        self.assertEqual(next_time.weekday(), 4)
        self.assertEqual(next_time.day, 12)

    def test_scrum_recurrence(self):
        # June 11, 2026 is a Thursday
        alarm_time = datetime(2026, 6, 11, 10, 0, 0)
        alarm = self.Alarm.create({
            'name': 'Scrum Alarm',
            'alarm_time': alarm_time,
            'recurrence_type': 'scrum',
            'user_id': self.user.id,
        })
        
        next_time = alarm._get_next_recurrence_datetime()
        # Next scrum recurrence (Mon-Thu + Sun) from Thursday should be Sunday (June 14, 2026, weekday index 6)
        self.assertEqual(next_time.weekday(), 6)
        self.assertEqual(next_time.day, 14)
