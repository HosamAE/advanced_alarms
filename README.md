# Advanced Alarms & Time Management
# نظام التنبيهات المتقدم وإدارة الوقت

<div align="center">

![Module Icon](static/description/icon.png)

**A powerful, self-contained productivity module for Odoo 19**

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-875A7B?style=flat-square&logo=odoo)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-Custom_Attribution-orange?style=flat-square)](LICENSE)
[![Author](https://img.shields.io/badge/Author-HosamAE-00D4FF?style=flat-square)](https://www.linkedin.com/in/hossameldeen-eissa/)
[![Category](https://img.shields.io/badge/Category-Productivity-7B2FFF?style=flat-square)](#)

*Smart Alarms · Countdown Timers · Multi-Lap Stopwatches · World Clocks*

</div>

---

## 📋 Overview

**Advanced Alarms & Time Management** brings a complete time management suite directly into Odoo's interface. Built from the ground up for Odoo 19 with OWL 2 components, it provides a rich systray experience with real-time notifications, customisable sounds, and intelligent data retention — all without any external dependencies.

---

## ⚡ Features at a Glance

| Feature | Details |
|---|---|
| 🔔 **Smart Alarms** | One-time or recurring, 4 priority levels (Critical → Low) |
| ⏱ **Timers** | Countdown with HH:MM:SS widget, multiple simultaneous timers |
| ⏲ **Stopwatches** | Multi-lap, persist across refreshes, live systray display |
| 🌐 **World Clocks** | Pre-configured major time zones, live in systray |
| 🔊 **Custom Sounds** | 5 built-in + upload your own MP3/OGG per alarm |
| 🛡 **Role Security** | Granular groups — Alarm Manager, Timer User, Stopwatch User |
| 📱 **Mobile Ready** | Fully responsive via SCSS media queries |
| 🌗 **RTL / LTR** | Bidirectional — Arabic & English without config |
| 🧹 **Auto Cleanup** | Periodic reminder to purge old records, keeps DB lean |

---

## 🔔 Alarms

- Create alarms with **priority levels**: `critical`, `high`, `normal`, `low`
- **Past alarms** appear muted (greyed-out) in the systray; **upcoming** show with vibrant colour
- **Critical alarms** trigger a full-screen-overlay notification that takes visual precedence
- Assign alarms to specific users; they receive real-time browser notifications
- Attach alarms to **any Odoo record** (e.g., a sale order, project task) with a direct link back to that record
- Configure **recurrence** (daily, weekly, specific weekdays) with an intuitive weekday selector widget
- Pre-alarms auto-dismiss after configurable grace period

## ⏱ Timers

- Enter duration using an intuitive **hours : minutes : seconds** picker widget
- Multiple timers run simultaneously, stacked neatly in the systray
- Timer cards colour-coded: `cyan` for running, `orange` for paused, `green` for completed
- Auto-dismiss completed timers after configurable delay
- Persistent: page refresh does **not** reset running timers

## ⏲ Stopwatches

- Start/Pause/Reset + **Lap** recording with sub-second precision
- Multiple concurrent stopwatches allowed
- Remain visible in systray until **manually** dismissed
- Lap history viewable inline in the systray dropdown

## 🌐 World Clocks

- Pre-loaded clocks for **New York, London, Dubai, Riyadh, Karachi, Mumbai, Singapore, Tokyo, Sydney**
- Automatically handles Daylight Saving Time (DST)
- Displayed live in the systray panel — always visible at a glance

---

## 🏗 Technical Architecture

```
advanced_alarms/
├── models/
│   ├── advanced_alarm.py          # Core alarm model, recurrence, bus notifications
│   ├── advanced_timer.py          # Timer model with countdown logic
│   ├── advanced_stopwatch.py      # Stopwatch model with lap tracking
│   ├── advanced_stopwatch_lap.py  # Lap record model
│   ├── advanced_alarm_sound.py    # Sound file storage model
│   ├── advanced_world_clock.py    # World clock configuration
│   ├── res_users.py               # User preference extensions
│   ├── res_company.py             # Company-level defaults
│   └── res_config_settings.py     # Settings panel integration
├── static/src/
│   ├── js/
│   │   ├── systray_item.js        # Main OWL systray component
│   │   ├── time_picker_widget.js  # HH:MM:SS duration widget
│   │   ├── weekday_selector_widget.js # Recurrence day picker
│   │   ├── stopwatch_widget.js    # Stopwatch OWL component
│   │   └── alarm_preview_widget.js # Alarm preview popup
│   ├── xml/                       # OWL templates (QWeb)
│   └── scss/alarms.scss           # All styling — glassmorphism, animations, RTL
├── views/                         # Odoo backend XML views
├── security/                      # Groups, ACL, record rules
├── data/                          # Default world clock data
├── tests/                         # Unit & integration tests
├── static/description/            # App Store assets
│   ├── icon.png                   # 512×512 store icon
│   ├── icon.svg                   # Vector source icon
│   ├── banner.png                 # Promotional banner
│   └── index.html                 # App Store description page
├── hooks.py                       # Post-install hook
├── LICENSE                        # Custom Attribution License
└── __manifest__.py
```

---

## 🛡 Security & Access Control

| Group | Access |
|---|---|
| `Advanced Alarms / Manager` | Full CRUD on all alarm records + configuration |
| `Advanced Alarms / Alarm User` | Create/edit own alarms; view assigned alarms |
| `Advanced Alarms / Timer User` | Create/manage own timers only |
| `Advanced Alarms / Stopwatch User` | Create/manage own stopwatches only |
| `Advanced Alarms / World Clock Viewer` | Read-only world clocks |

> Record rules ensure each user sees **only their own** records unless they are a Manager.

---

## 📦 Installation

1. Copy the `advanced_alarms` folder into your Odoo addons path.
2. Restart Odoo server: `./odoo-bin -u all` or restart the service.
3. Go to **Settings → Activate Developer Mode**.
4. Navigate to **Apps → Update App List**, then search for **Advanced Alarms**.
5. Click **Install**.
6. Assign the appropriate groups to your users under **Settings → Users**.

---

## ⚙️ Configuration

Go to **Settings → Technical → Advanced Alarms Settings**:

- **Retention Period** — how long completed alarm/timer records are kept before the cleanup warning triggers
- **Cleanup Warning Threshold** — number of days before a reminder notification is sent
- **Default Sound** — fallback sound for alarms/timers without a custom sound
- **Auto-dismiss Delay** — seconds before a completed timer card auto-disappears from systray

Each user can also override preferences in their **Profile → Alarm Preferences** tab.

---

## 🧪 Testing

The module includes a comprehensive test suite:

```bash
# Run all module tests
python odoo-bin -d <database> --test-enable --stop-after-init -i advanced_alarms

# Test files
tests/test_advanced_alarms.py   # Alarm creation, recurrence, priority, notifications
tests/test_recurrence.py        # Recurrence logic edge cases
```

---

## 📝 Changelog

### v19.0.1.0.0 — June 2026 (Initial Release)
- ✅ Full alarm system with 4 priority levels and recurrence rules
- ✅ Countdown timers with HH:MM:SS widget
- ✅ Multi-lap stopwatches with persistence
- ✅ World clock integration with DST support
- ✅ Custom sound upload support (MP3 / OGG)
- ✅ Role-based security with record rules
- ✅ Mobile-responsive SCSS
- ✅ Memory-leak-safe OWL 2 components (willUnmount cleanup)
- ✅ RTL / LTR full support
- ✅ Automated data cleanup reminders
- ✅ Linked model navigation (alarm → record)

---

## ⚖️ License

This module is released under the **Advanced Alarms Custom Attribution License**.

**✅ Allowed:**
- Free use in commercial and personal Odoo projects
- Modification of source code for internal use
- Submitting improvements/bug-fixes back to the author

**❌ NOT Allowed:**
- Re-publishing or listing under a different author name on any marketplace
- Removing or altering copyright notices in any file
- Claiming ownership of original or derived work
- Selling as a standalone product without written consent

Any externally distributed derived work **must** include:
> *"Based on Advanced Alarms & Time Management — Original Author: HosamAE"*

See the full [LICENSE](LICENSE) file for complete terms.

---

## 👨‍💻 Author

<div align="center">

**HosamAE — Hossam A. Eissa**  
*Odoo Developer & Software Engineer*

[![Email](https://img.shields.io/badge/Email-HossamA.Eissa%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:HossamA.Eissa@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Hossam_Eldeen_Eissa-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hossameldeen-eissa/)

*If this module helps you, a ⭐ star and a LinkedIn connection are always appreciated!*

</div>

---

<div align="center">
  <sub>© 2024–2026 HosamAE. All rights reserved.</sub>
</div>
