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

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillStart, onWillDestroy } from "@odoo/owl";

export class StopwatchTimerWidget extends Component {
    setup() {
        this.state = useState({
            formattedTime: "00:00:00",
        });
        
        this.ticker = null;

        onWillStart(() => {
            this.updateTime();
            this.startTicker();
        });

        onWillDestroy(() => {
            this.stopTicker();
        });
    }

    get record() {
        return this.props.record;
    }

    startTicker() {
        if (!this.ticker) {
            this.ticker = setInterval(() => {
                this.updateTime();
            }, 100);
        }
    }

    stopTicker() {
        if (this.ticker) {
            clearInterval(this.ticker);
            this.ticker = null;
        }
    }

    updateTime() {
        const state = this.record.data.state;
        const accumulated = this.record.data.accumulated_paused || 0;
        let elapsed = 0;

        if (state === 'running' && this.record.data.start_time) {
            // start_time is a luxon DateTime in Odoo 17
            const startTime = this.record.data.start_time.toJSDate();
            // In backend form, time is usually UTC or local? toJSDate() handles it correctly as local if luxon was properly initialized.
            // Wait, Odoo fields.Datetime are in UTC, and luxon DateTime objects in UI are in local timezone.
            // Let's just use diff from now.
            const now = new Date();
            const diffSeconds = (now.getTime() - startTime.getTime()) / 1000;
            elapsed = Math.floor(diffSeconds) - accumulated;
        } else if (state === 'paused' && this.record.data.start_time && this.record.data.paused_time) {
            const startTime = this.record.data.start_time.toJSDate();
            const pausedTime = this.record.data.paused_time.toJSDate();
            const diffSeconds = (pausedTime.getTime() - startTime.getTime()) / 1000;
            elapsed = Math.floor(diffSeconds) - accumulated;
        } else {
            elapsed = 0;
        }

        if (elapsed < 0) elapsed = 0;

        const h = Math.floor(elapsed / 3600).toString().padStart(2, '0');
        const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
        const s = Math.floor(elapsed % 60).toString().padStart(2, '0');
        
        this.state.formattedTime = `${h}:${m}:${s}`;
    }
}

StopwatchTimerWidget.template = "advanced_alarms.StopwatchTimerWidget";
StopwatchTimerWidget.props = {
    ...standardFieldProps,
};

export const stopwatchTimerField = {
    component: StopwatchTimerWidget,
    supportedTypes: ["char"],
};

// Register the field widget
registry.category("fields").add("stopwatch_timer", stopwatchTimerField);
