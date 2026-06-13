/** @odoo-module */
/*
 * Advanced Alarms & Time Management — Odoo 17
 * Copyright (c) 2024-2026 HosamAE (Hossam A. Eissa)
 * Email   : HossamA.Eissa@gmail.com
 * LinkedIn: https://www.linkedin.com/in/hossameldeen-eissa/
 *
 * Licensed under the Custom Attribution License — see LICENSE file.
 * Free to use and modify; NOT allowed to re-publish under a different author name.
 */

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { Dropdown } from "@web/core/dropdown/dropdown";

// Format helper to pad numbers
function pad(num, size = 2) {
    let s = num + "";
    while (s.length < size) s = "0" + s;
    return s;
}

export class AdvancedAlarmsSystrayItem extends Component {
    static template = "advanced_alarms.SystrayItem";
    static components = { Dropdown };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.busService = this.env.services.bus_service;

        // Static configuration lists
        this.worldTimezones = [
            { name: "London (GMT)", tz: "Europe/London" },
            { name: "New York (EST)", tz: "America/New_York" },
            { name: "Tokyo (JST)", tz: "Asia/Tokyo" },
            { name: "Cairo/Riyadh (EET/AST)", tz: "Asia/Riyadh" },
            { name: "Sydney (AEST)", tz: "Australia/Sydney" }
        ];
        
        // Define reactive state
        this.state = useState({
            counter: 0,
            activeTab: 'alarm', // 'alarm', 'world_clock', 'timer', 'stopwatch'
            alarms: [],
            timers: [],
            stopwatches: [],
            notifications: [],
            worldClocks: [], // Dynamic world clocks from backend
            isLocalClockPinned: localStorage.getItem('advanced_alarms_local_clock_pinned') === 'true',
            hasActiveRinging: false,
            direction: 'bottom-right', // position class
            userSettings: {
                alarm_ring_duration: 60,
                timer_ring_repeat: 3,
                pre_alarm_duration: 5,
                notif_dismiss_duration: 5,
                notif_position: 'auto',
                snooze_duration: 5,
                snooze_limit: 3,
                stopwatch_alert_interval: 3600,
            },
            now: Date.now(),
        });

        this.stopwatchAlertPeriods = {};

        // Cache for DateTimeFormatters to improve performance
        this.tzFormatters = {};

        this.notificationIdCounter = 0;
        this.activeAudioInstances = {}; // Map of notification ID to Audio object
        this.ticker = null;

        onWillStart(async () => {
            await this.loadUserSettings();
            await this.loadData();
            
            // Connect to bus channel
            const channel = `advanced_alarms_${session.uid}`;
            this.busService.addChannel(channel);
            this.busService.addEventListener("notification", this.onBusNotification.bind(this));
            
            // Start the tick timer (every 100ms for smooth UI animations/stopwatch)
            this.ticker = setInterval(() => this.tick(), 100);
        });

        onWillUnmount(() => {
            if (this.ticker) {
                clearInterval(this.ticker);
            }
            // Stop any playing sounds
            Object.values(this.activeAudioInstances).forEach(audio => {
                try { audio.pause(); } catch(e){}
            });
        });
    }

    // Helper to get cached formatter
    getTzFormatter(tz) {
        if (!this.tzFormatters[tz]) {
            this.tzFormatters[tz] = new Intl.DateTimeFormat('en-US', {
                timeZone: tz,
                year: 'numeric', month: 'numeric', day: 'numeric',
                hour: 'numeric', minute: 'numeric', second: 'numeric',
                hour12: false,
            });
        }
        return this.tzFormatters[tz];
    }

    // Apply offset and return local date object holding target time
    getShiftedDate(tz, offsetMinutes) {
        const formatter = this.getTzFormatter(tz);
        const parts = formatter.formatToParts(new Date());
        const getPart = (type) => parseInt(parts.find(p => p.type === type).value);
        
        return new Date(
            getPart('year'),
            getPart('month') - 1, // JS months are 0-indexed
            getPart('day'),
            getPart('hour'),
            getPart('minute') + (offsetMinutes || 0),
            getPart('second')
        );
    }

    getCityTime(tz, offsetMinutes = 0) {
        if (tz === 'local') {
            return new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true }).format(new Date());
        }
        try {
            const localDate = this.getShiftedDate(tz, offsetMinutes);
            return new Intl.DateTimeFormat('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            }).format(localDate);
        } catch (e) {
            return '--:--:--';
        }
    }

    getCityDate(tz, offsetMinutes = 0) {
        if (tz === 'local') {
            return new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }).format(new Date());
        }
        try {
            const localDate = this.getShiftedDate(tz, offsetMinutes);
            return new Intl.DateTimeFormat('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            }).format(localDate);
        } catch (e) {
            return '--/--/----';
        }
    }

    // Cycle DST manually (Auto -> +1h -> -1h)
    // NOTE: In the new architecture, users might just change dst_mode from backend.
    // Or we can add an RPC call here to update the user's personal offset if desired.
    // For now, we will leave it as local state override until next reload.
    cycleDst(clock) {
        if (!clock.dstOffset) {
            clock.dstOffset = 60; // +1 hour
        } else if (clock.dstOffset === 60) {
            clock.dstOffset = -60; // -1 hour
        } else {
            clock.dstOffset = 0; // Auto / Reset
        }
    }

    async loadUserSettings() {
        try {
            const settings = await this.orm.call("advanced.alarm", "get_time_management_settings");
            if (settings) {
                this.state.userSettings = settings;
            }
            // No need to load floatingClocks from userSettings anymore
            this.updateBadgeCounter();
            this.updateDirectionAndPosition();
        } catch (error) {
            console.error("Failed to load user settings:", error);
        }
    }

    updateDirectionAndPosition() {
        const posSetting = this.state.userSettings.notif_position || 'auto';
        let dirClass = 'bottom-right';
        if (posSetting === 'auto') {
            const isRtl = document.documentElement.dir === 'rtl';
            dirClass = isRtl ? 'bottom-left' : 'bottom-right';
        } else {
            dirClass = posSetting.replace('_', '-');
        }
        this.state.direction = dirClass;
    }



    async loadData() {
        try {
            const alarms_data = await this.orm.call("advanced.alarm", "get_todays_alarms");
            const timers = await this.orm.call("advanced.timer", "get_active_timers");
            const stopwatches = await this.orm.call("advanced.stopwatch", "get_active_stopwatches");
            const worldClocks = await this.orm.call("advanced.alarm", "get_world_clocks");

            // Parse stopwatch splits
            stopwatches.forEach(sw => {
                try {
                    sw.split_times_parsed = JSON.parse(sw.split_times || '[]');
                } catch (e) {
                    sw.split_times_parsed = [];
                }
            });

            this.state.alarms = alarms_data.alarms;
            this.state.old_muted_count = alarms_data.old_muted_count;
            this.state.timers = timers;
            this.state.stopwatches = stopwatches;
            
            // Map backend dst_mode to local dstOffset
            worldClocks.forEach(c => {
                if (c.dst_mode === 'force_add') c.dstOffset = 60;
                else if (c.dst_mode === 'force_sub') c.dstOffset = -60;
                else c.dstOffset = 0;
            });
            this.state.worldClocks = worldClocks;

            this.updateBadgeCounter();
        } catch (error) {
            console.error("Failed to load alarm/timer data:", error);
        }
    }

    updateBadgeCounter() {
        // Count active ringing alarms + running timers
        const ringingCount = this.state.alarms.filter(a => a.state === 'active').length;
        const runningTimers = this.state.timers.filter(t => t.state === 'running').length;
        this.state.counter = ringingCount + runningTimers;
        this.state.hasActiveRinging = ringingCount > 0;
    }

    // Bus listener
    onBusNotification({ detail }) {
        let shouldReload = false;
        for (const message of detail) {
            if (message.type === 'notification' && message.payload) {
                const payload = message.payload;
                if (payload.type === 'alarm_update') {
                    shouldReload = true;
                } else if (payload.type === 'timer_update') {
                    shouldReload = true;
                } else if (payload.type === 'stopwatch_update') {
                    shouldReload = true;
                } else if (payload.type === 'cleanup_reminder') {
                    this.addNotification({
                        title: "Workspace Cleanup",
                        message: payload.message,
                        type: 'stopwatch',
                        is_critical: false,
                        expires: true,
                        expire_duration: 10,
                    });
                }
            }
        }
        if (shouldReload) {
            this.loadData();
        }
    }

    onBeforeOpen() {
        this.loadUserSettings();
        this.loadData();
    }

    switchTab(tabName) {
        this.state.activeTab = tabName;
    }

    // Adapt Create New behavior based on the active tab
    onCreateNew() {
        let model = "advanced.alarm";
        let title = "Create Alarm";
        
        if (this.state.activeTab === 'timer') {
            model = "advanced.timer";
            title = "Create Timer";
        } else if (this.state.activeTab === 'stopwatch') {
            model = "advanced.stopwatch";
            title = "Create Stopwatch";
        }

        this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: model,
            views: [[false, "form"]],
            target: "new",
        });
    }

    // Main clock loop checking alarms, timers, stopwatches
    tick() {
        const now = new Date();
        this.state.now = now.getTime(); // Make UI reactive
        
        // Update floating clock dynamic time display
        const nowLuxon = luxon.DateTime.now();
        this.state.floatingClockTime = nowLuxon.toFormat('hh:mm:ss a');
        this.state.floatingClockDate = nowLuxon.toFormat('EEE, MMM dd, yyyy');

        // Check alarm ring duration limit (in seconds)
        const limitSec = parseInt(this.state.userSettings.alarm_ring_duration) || 60;
        Object.keys(this.activeAudioInstances).forEach(notifIdStr => {
            const notifId = parseInt(notifIdStr);
            const notif = this.state.notifications.find(n => n.id === notifId);
            if (notif && notif.type === 'alarm' && notif.soundStartTime) {
                const elapsedSec = (now - notif.soundStartTime) / 1000;
                if (elapsedSec >= limitSec) {
                    this.closeNotification(notifId);
                }
            }
        });

        // Update live countdowns for scramble alerts
        this.state.notifications.forEach(n => {
            if (n.type === 'scramble_alert' && n.target_date) {
                const diffMs = n.target_date - now;
                if (diffMs > 0) {
                    const h = Math.floor(diffMs / 3600000);
                    const m = Math.floor((diffMs % 3600000) / 60000);
                    const s = Math.floor((diffMs % 60000) / 1000);
                    const ms = Math.floor((diffMs % 1000) / 10);
                    n.time_text = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms).padStart(2,'0')}`;
                } else {
                    n.time_text = "00:00:00.00";
                }
            }
        });

        // 1. Check Alarms
        this.state.alarms.forEach(alarm => {
            if (alarm.state === 'done' || alarm.state === 'muted') return;

            const alarmTime = this.parseOdooDatetime(alarm.alarm_time);
            if (!alarmTime) return;

            const diffMs = alarmTime - now;

            // Trigger PRE-ALARM: if pre-alarm is active, not sent yet, and within duration
            if (alarm.pre_alarm && alarm.state === 'pending') {
                const preDurationMs = (this.state.userSettings.pre_alarm_duration || 5) * 60 * 1000;
                if (diffMs > 0 && diffMs <= preDurationMs) {
                    this.triggerPreAlarm(alarm);
                }
            }

            // Trigger MAIN ALARM: time reached
            if (diffMs <= 0 && alarm.state !== 'active') {
                this.triggerMainAlarm(alarm);
            }
        });

        // 2. Check Timers
        this.state.timers.forEach(timer => {
            if (timer.state !== 'running') return;
            const remaining = this.getTimerRemainingSeconds(timer);
            if (remaining <= 0) {
                this.triggerTimerDone(timer);
            }
        });

        // 3. Check Stopwatches (for periodic alerts)
        this.state.stopwatches.forEach(sw => {
            if (sw.state !== 'running') return;
            const elapsed = this.getStopwatchElapsedSeconds(sw);
            
            // Check if alert interval is reached and check against last alert time
            const interval = sw.alert_interval || this.state.userSettings.stopwatch_alert_interval || 3600;
            const currentPeriod = Math.floor(elapsed / interval);
            
            if (currentPeriod > 0 && this.stopwatchAlertPeriods[sw.id] === undefined) {
                this.stopwatchAlertPeriods[sw.id] = 0;
            }

            if (currentPeriod > 0 && currentPeriod > this.stopwatchAlertPeriods[sw.id]) {
                this.stopwatchAlertPeriods[sw.id] = currentPeriod;
                this.triggerStopwatchAlert(sw, elapsed);
            }
        });
    }

    // Convert Odoo datetime string (UTC) to browser Date object
    parseOdooDatetime(dtStr) {
        if (!dtStr) return null;
        // dtStr is in 'YYYY-MM-DD HH:MM:SS' UTC format
        // append Z to treat it as UTC
        const utcStr = dtStr.replace(" ", "T") + "Z";
        return new Date(utcStr);
    }

    // Trigger silent pre-alarm that auto-dismisses (or scramble live alert)
    triggerPreAlarm(alarm) {
        // Temporarily write to state to prevent re-triggering
        alarm.state = 'pre_alarm';
        // Notify backend of status change (to keep sync)
        this.orm.write("advanced.alarm", [alarm.id], { state: 'pre_alarm' });

        const isScramble = (alarm.recurrence_type === 'scrum');
        const targetDate = this.parseOdooDatetime(alarm.alarm_time);
        const timeRemaining = Math.max(0, Math.ceil((targetDate - new Date()) / 60000));
        const dismissDuration = this.state.userSettings.notif_dismiss_duration || 5;
        
        const notifId = this.addNotification({
            title: isScramble ? `Live Alert: ${alarm.name}` : `Pre-alarm: ${alarm.name}`,
            message: isScramble ? `Countdown to event` : `Starts in ${timeRemaining} minutes.`,
            type: isScramble ? 'scramble_alert' : 'pre-alarm',
            is_critical: alarm.is_critical,
            expires: !isScramble,
            expire_duration: dismissDuration,
            res_model: alarm.res_model,
            res_id: alarm.res_id,
            time_text: isScramble ? '...' : `${timeRemaining}m left`,
            target_date: targetDate, // For live countdown
            alarm_id: alarm.id,
        });

        // Play notification click for pre-alarms
        if (this.state.userSettings.notif_sound_src) {
            this.playSound(notifId, this.state.userSettings.notif_sound_src, false, 1);
        }
    }

    // Trigger main ringing alarm
    triggerMainAlarm(alarm) {
        alarm.state = 'active';
        this.orm.write("advanced.alarm", [alarm.id], { state: 'active' });
        this.updateBadgeCounter();

        // Create alarm notification
        const notifId = this.addNotification({
            title: alarm.name,
            message: alarm.message || "Reminder!",
            type: 'alarm',
            is_critical: alarm.is_critical,
            expires: false, // does not disappear until clicked X
            res_model: alarm.res_model,
            res_id: alarm.res_id,
            time_text: "Ringing...",
            alarm_db_id: alarm.id,
            is_ringing: true,
        });

        // Play Sound
        if (alarm.sound_src) {
            this.playSound(notifId, alarm.sound_src, true); // Loop sound
        }
    }

    // Trigger when a timer completes
    triggerTimerDone(timer) {
        timer.state = 'done';
        this.orm.call("advanced.timer", "action_done", [timer.id]);
        this.updateBadgeCounter();

        const notifId = this.addNotification({
            title: `Timer Completed: ${timer.name}`,
            message: "Time is up!",
            type: 'timer',
            is_critical: true, // Timers are treated as critical on completion
            expires: false, // requires manual X
            sound_src: timer.sound_src,
            res_model: 'advanced.timer',
            res_id: timer.id,
            time_text: "Time's up!",
            timer_db_id: timer.id,
            is_ringing: true,
        });

        if (timer.sound_src) {
            const repeats = this.state.userSettings.timer_ring_repeat || 3;
            const soundSrc = this.state.userSettings.timer_sound_src || timer.sound_src;
            this.playSound(notifId, soundSrc, true, repeats);
        }
    }

    // Trigger periodic alert for stopwatch
    triggerStopwatchAlert(sw, elapsed) {
        const timeStr = this.formatDuration(Math.floor(elapsed));
        const dismissDuration = this.state.userSettings.notif_dismiss_duration || 5;
        this.addNotification({
            title: `Stopwatch: ${sw.name}`,
            message: `Elapsed time: ${timeStr}`,
            type: 'stopwatch',
            is_critical: false,
            expires: true,
            expire_duration: dismissDuration,
        });
    }

    // Helper to add notification to reactive list
    addNotification(config) {
        this.notificationIdCounter++;
        const id = this.notificationIdCounter;
        
        const notif = {
            id,
            title: config.title,
            message: config.message,
            type: config.type,
            is_critical: config.is_critical,
            expires: config.expires,
            expire_duration: config.expire_duration || 5,
            res_model: config.res_model,
            res_id: config.res_id,
            time_text: config.time_text,
            alarm_db_id: config.alarm_db_id,
            soundStartTime: new Date(),
        };

        this.state.notifications.push(notif);

        // Auto-dismiss setup
        if (config.expires) {
            setTimeout(() => {
                this.closeNotification(id);
            }, notif.expire_duration * 1000);
        }

        return id;
    }

    closeNotification(id) {
        const notif = this.state.notifications.find(n => n.id === id);
        if (!notif) return;

        // If linked to alarm, mark it as done/muted in DB when closed
        if (notif.alarm_db_id) {
            this.orm.call("advanced.alarm", "action_done", [notif.alarm_db_id]);
        }

        // Stop sound
        if (this.activeAudioInstances[id]) {
            try {
                this.activeAudioInstances[id].pause();
                delete this.activeAudioInstances[id];
            } catch(e){}
        }

        // Remove from UI
        this.state.notifications = this.state.notifications.filter(n => n.id !== id);
        this.loadData(); // reload timeline to sync statuses
    }

    // Sound manager supporting loops and repeats
    playSound(notifId, src, loop = false, maxRepeats = 1) {
        const audio = new Audio(src);
        if (loop && maxRepeats > 1) {
            let playCount = 1;
            audio.addEventListener('ended', () => {
                playCount++;
                if (playCount <= maxRepeats) {
                    audio.play().catch(e => console.warn(e));
                } else {
                    audio.pause();
                }
            });
        } else {
            audio.loop = loop;
        }
        audio.play().catch(err => {
            console.warn("Audio play blocked by browser autoplay policy", err);
        });
        this.activeAudioInstances[notifId] = audio;
    }

    // Floating Clock Toggle
    async toggleFloatingClock(clock_id) {
        if (clock_id === 'local') {
            this.state.isLocalClockPinned = !this.state.isLocalClockPinned;
            localStorage.setItem('advanced_alarms_local_clock_pinned', this.state.isLocalClockPinned);
            return;
        }
        
        const clock = this.state.worldClocks.find(c => c.id === clock_id);
        if (clock) {
            // Optimistic update
            clock.is_pinned = !clock.is_pinned;
            
            // Backend update
            try {
                await this.orm.call("advanced.alarm", "toggle_pinned_clock", [clock_id]);
            } catch (e) {
                console.error("Failed to toggle pinned clock", e);
                // Revert if failed
                clock.is_pinned = !clock.is_pinned;
            }
        }
    }

    isClockFloating(clock_id) {
        if (clock_id === 'local') return this.state.isLocalClockPinned;
        const clock = this.state.worldClocks.find(c => c.id === clock_id);
        return clock ? clock.is_pinned : false;
    }

    // World Clock cities timezone helper
    // (getCityTime and getCityDate removed because they were replaced with Intl versions at the top)

    getCityOffset(tzName) {
        const local = luxon.DateTime.now();
        const city = luxon.DateTime.now().setZone(tzName);
        const diffHours = (city.offset - local.offset) / 60;
        if (diffHours === 0) return "Same time";
        return (diffHours > 0 ? "+" : "") + diffHours + " hrs";
    }

    getStopwatchLaps(sw) {
        if (!sw.split_times_parsed || sw.split_times_parsed.length === 0) return [];
        const laps = [];
        let prevSplit = 0;
        sw.split_times_parsed.forEach((split, index) => {
            const lapSeconds = split - prevSplit;
            laps.push({
                index: index + 1,
                lapTime: this.formatSeconds(Math.floor(lapSeconds)),
                totalTime: this.formatSeconds(Math.floor(split))
            });
            prevSplit = split;
        });
        return laps.reverse();
    }

    openRecord(model, id) {
        let title = "Edit Record";
        if (model === "advanced.alarm") title = "Edit Alarm";
        else if (model === "advanced.timer") title = "Edit Timer";
        else if (model === "advanced.stopwatch") title = "Edit Stopwatch";

        this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: model,
            res_id: id,
            views: [[false, "form"]],
            target: "new",
        });
    }

    // Snooze Alarm Action from notification card
    async snoozeNotificationAlarm(notif) {
        if (!notif.alarm_db_id) return;
        
        // Stop sound and remove notification first
        if (this.activeAudioInstances[notif.id]) {
            try {
                this.activeAudioInstances[notif.id].pause();
                delete this.activeAudioInstances[notif.id];
            } catch(e){}
        }
        this.state.notifications = this.state.notifications.filter(n => n.id !== notif.id);
        
        // Call backend snooze action
        await this.orm.call("advanced.alarm", "action_snooze", [notif.alarm_db_id]);
        await this.loadData();
    }

    // Formatting helpers for XML template
    formatAlarmTime(dtStr) {
        const dt = this.parseOdooDatetime(dtStr);
        if (!dt) return "";
        return pad(dt.getHours()) + ":" + pad(dt.getMinutes());
    }

    getTimerDisplay(timer) {
        const sec = this.getTimerRemainingSeconds(timer);
        return this.formatDuration(sec);
    }

    getTimerRemainingSeconds(timer) {
        if (timer.state === 'draft') return timer.duration;
        if (timer.state === 'done') return 0;
        
        const startTime = this.parseOdooDatetime(timer.start_time);
        if (!startTime) return timer.duration;

        const now = new Date(this.state.now);
        const elapsed = Math.floor((now - startTime) / 1000) - (timer.accumulated_paused || 0);
        
        if (timer.state === 'paused') {
            const pausedTime = this.parseOdooDatetime(timer.paused_time);
            const pauseElapsed = Math.floor((now - pausedTime) / 1000);
            return Math.max(0, timer.duration - elapsed + pauseElapsed);
        }

        return Math.max(0, timer.duration - elapsed);
    }

    getStopwatchDisplay(sw) {
        const sec = this.getStopwatchElapsedSeconds(sw);
        return this.formatStopwatchDuration(sec);
    }

    getStopwatchElapsedSeconds(sw) {
        if (sw.state === 'draft') return 0;
        
        const startTime = this.parseOdooDatetime(sw.start_time);
        if (!startTime) return 0;

        const now = new Date(this.state.now);
        let elapsedMs = (now - startTime) - (sw.accumulated_paused || 0) * 1000;

        if (sw.state === 'paused') {
            const pausedTime = this.parseOdooDatetime(sw.paused_time);
            const pauseElapsedMs = now - pausedTime;
            elapsedMs = elapsedMs - pauseElapsedMs;
        }

        return Math.max(0, elapsedMs / 1000);
    }

    formatDuration(totalSec) {
        const hrs = Math.floor(totalSec / 3600);
        const mins = Math.floor((totalSec % 3600) / 60);
        const secs = totalSec % 60;
        return (hrs > 0 ? pad(hrs) + ":" : "") + pad(mins) + ":" + pad(secs);
    }

    formatStopwatchDuration(totalSec) {
        const hrs = Math.floor(totalSec / 3600);
        const mins = Math.floor((totalSec % 3600) / 60);
        const secs = Math.floor(totalSec % 60);
        const ms = Math.floor((totalSec % 1) * 100);
        
        return (hrs > 0 ? pad(hrs) + ":" : "") + 
               pad(mins) + ":" + 
               pad(secs) + "." + 
               pad(ms);
    }

    formatSeconds(seconds) {
        return this.formatDuration(seconds);
    }

    // Backend Actions from UI Cards
    async markAlarmDone(id) {
        await this.orm.call("advanced.alarm", "action_done", [id]);
        this.loadData();
    }

    async muteAlarm(id) {
        await this.orm.call("advanced.alarm", "action_mute", [id]);
        this.loadData();
    }

    async deleteAlarm(id) {
        await this.orm.unlink("advanced.alarm", [id]);
        this.loadData();
    }

    async clearAllMuted() {
        await this.orm.call("advanced.alarm", "action_clear_muted_alarms");
        this.loadData();
    }

    async startTimer(id) {
        await this.orm.call("advanced.timer", "action_start", [id]);
        this.loadData();
    }

    async pauseTimer(id) {
        await this.orm.call("advanced.timer", "action_pause", [id]);
        this.loadData();
    }

    async resetTimer(id) {
        await this.orm.call("advanced.timer", "action_reset", [id]);
        this.loadData();
    }

    async deleteTimer(id) {
        await this.orm.unlink("advanced.timer", [id]);
        this.loadData();
    }

    async startStopwatch(id) {
        await this.orm.call("advanced.stopwatch", "action_start", [id]);
        this.loadData();
    }

    async pauseStopwatch(id) {
        await this.orm.call("advanced.stopwatch", "action_pause", [id]);
        this.loadData();
    }

    async lapStopwatch(id) {
        const sw = this.state.stopwatches.find(s => s.id === id);
        if (!sw) return;
        
        const elapsed = Math.floor(this.getStopwatchElapsedSeconds(sw));
        const splits = sw.split_times_parsed || [];
        const prevSplit = splits.length > 0 ? splits[splits.length - 1] : 0;
        const diff = elapsed - prevSplit;

        await this.orm.call("advanced.stopwatch", "action_add_lap", [[id], elapsed, diff]);
        this.loadData();
    }

    async resetStopwatch(id) {
        await this.orm.call("advanced.stopwatch", "action_reset", [id]);
        this.loadData();
    }

    async deleteStopwatch(id) {
        await this.orm.unlink("advanced.stopwatch", [id]);
        this.loadData();
    }



    openLinkedRecord(resModel, resId) {
        if (!resModel || !resId) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

// Register as a Systray component
export const systrayItem = {
    Component: AdvancedAlarmsSystrayItem,
};

registry.category("systray").add("advanced_alarms.SystrayItem", systrayItem, { sequence: 15 });

