{
    'name': 'Advanced Alarms & Time Management',
    'version': '18.0.1.0.0',
    'summary': 'Smart Alarms, Timers & Stopwatches with Systray Integration',
    'description': """
        Advanced Alarms & Time Management
        ==================================
        A powerful productivity module for Odoo 18 that brings a full-featured
        time management suite directly into your Odoo interface.

        ✅ Key Features:
        ─────────────────────────────────────────────────────────────────
        🔔  Smart Alarms     — One-time or recurring, with critical priority
        ⏱   Timers           — Countdown timers with a beautiful HH:MM:SS widget
        ⏲   Stopwatches      — Multi-lap stopwatches, always visible in systray
        🌐  World Clocks     — Monitor multiple time-zones at a glance
        🔊  Custom Sounds    — Non-musical notification sounds per alarm/timer
        📱  Mobile Ready     — Fully responsive, optimised for small screens
        🛡   Role Security   — Granular access groups per feature
        🌗  RTL / LTR       — Full Arabic & English bidirectional support
        ─────────────────────────────────────────────────────────────────

        Author  : HosamAE (Hossam A. Eissa)
        Email   : HossamA.Eissa@gmail.com
        LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
        License : Custom Attribution License (see LICENSE file)
    """,
    'category': 'Productivity/Time Management',
    'author': 'HosamAE',
    'maintainer': 'HosamAE',
    'website': 'https://www.linkedin.com/in/hossameldeen-eissa/',
    'support': 'HossamA.Eissa@gmail.com',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'mail', 'web', 'bus'],
    'data': [
        'data/advanced_world_clock_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/advanced_alarm_views.xml',
        'views/res_users_views.xml',
        'views/res_config_settings_views.xml',
        'views/advanced_world_clock_views.xml',
        'data/advanced_alarm_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'advanced_alarms/static/src/scss/alarms.scss',
            'advanced_alarms/static/src/js/systray_item.js',
            'advanced_alarms/static/src/js/time_picker_widget.js',
            'advanced_alarms/static/src/js/weekday_selector_widget.js',
            'advanced_alarms/static/src/js/stopwatch_widget.js',
            'advanced_alarms/static/src/js/alarm_preview_widget.js',
            'advanced_alarms/static/src/xml/systray_item.xml',
            'advanced_alarms/static/src/xml/stopwatch_widget.xml',
            'advanced_alarms/static/src/xml/alarm_preview_widget.xml',
        ],
        'web.assets_web_dark': [
            'advanced_alarms/static/src/scss/alarms.dark.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'post_init_hook': 'post_init_hook',
}
