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

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { localization } from "@web/core/l10n/localization";
import { deserializeDateTime } from "@web/core/l10n/dates";

const { DateTime } = luxon;

export class TimePickerField extends Component {
    static template = "advanced_alarms.TimePickerField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({ 
            hour: "00", 
            minute: "00", 
            ampm: "AM",
            showHourDropdown: false, 
            showMinuteDropdown: false,
            showAmPmDropdown: false
        });

        onWillStart(() => {
            this.initTime();
        });
    }

    initTime() {
        const val = this.props.record.data[this.props.name];
        let dt;
        if (val) {
            dt = deserializeDateTime(val);
        }
        if (!dt || !dt.isValid) {
            dt = DateTime.local();
        }
        if (this.is12Hour) {
            let h12 = dt.hour % 12;
            if (h12 === 0) h12 = 12;
            this.state.hour = h12.toString().padStart(2, '0');
            this.state.ampm = dt.hour >= 12 ? "PM" : "AM";
        } else {
            this.state.hour = dt.hour.toString().padStart(2, '0');
        }
        this.state.minute = dt.minute.toString().padStart(2, '0');
    }

    get is12Hour() {
        const timeFormatPref = session.advanced_alarms_time_format || 'system';
        if (timeFormatPref === '12h') {
            return true;
        } else if (timeFormatPref === '24h') {
            return false;
        } else {
            return localization.timeFormat.includes("a") || localization.timeFormat.includes("A") || localization.timeFormat.includes("p");
        }
    }

    get formattedTime() {
        const val = this.props.record.data[this.props.name];
        if (val) {
            const dt = deserializeDateTime(val);
            if (dt && dt.isValid) {
                return dt.toFormat(localization.timeFormat);
            }
        }
        return "";
    }

    onTimeChange() {
        let h = parseInt(this.state.hour, 10);
        let m = parseInt(this.state.minute, 10);
        
        if (isNaN(h)) h = 0;
        if (isNaN(m)) m = 0;
        
        if (this.is12Hour) {
            if (h > 12) h = 12;
            if (h < 1) h = 1;
        } else {
            if (h > 23) h = 23;
            if (h < 0) h = 0;
        }
        
        if (m > 59) m = 59;
        if (m < 0) m = 0;
        
        // Re-pad the state
        this.state.hour = h.toString().padStart(2, '0');
        this.state.minute = m.toString().padStart(2, '0');
        
        let actualHour = h;
        if (this.is12Hour) {
            if (this.state.ampm === "PM" && h < 12) actualHour = h + 12;
            if (this.state.ampm === "AM" && h === 12) actualHour = 0;
        }
        
        const val = this.props.record.data[this.props.name];
        let baseDate;
        if (val) {
            baseDate = deserializeDateTime(val);
        }
        if (!baseDate || !baseDate.isValid) {
            baseDate = DateTime.local();
        }

        const updatedVal = baseDate.set({
            hour: actualHour,
            minute: m,
            second: 0,
            millisecond: 0
        });

        this.props.record.update({ [this.props.name]: updatedVal });
    }

    setHour(h) {
        this.state.hour = h.toString().padStart(2, '0');
        this.state.showHourDropdown = false;
        this.onTimeChange();
    }

    setMinute(m) {
        this.state.minute = m.toString().padStart(2, '0');
        this.state.showMinuteDropdown = false;
        this.onTimeChange();
    }

    setAmPm(val) {
        this.state.ampm = val;
        this.state.showAmPmDropdown = false;
        this.onTimeChange();
    }

    onHourBlur() {
        this.state.showHourDropdown = false;
        this.onTimeChange();
    }

    onMinuteBlur() {
        this.state.showMinuteDropdown = false;
        this.onTimeChange();
    }
    
    onAmPmBlur() {
        this.state.showAmPmDropdown = false;
        this.onTimeChange();
    }
}

export const timePickerField = {
    component: TimePickerField,
    displayName: "Time Picker",
    supportedTypes: ["datetime"],
    isEmpty: (value) => value === false || value === null || value === "",
};

registry.category("fields").add("time_picker_widget", timePickerField);
