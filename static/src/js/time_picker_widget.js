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
import { Component, useState, useExternalListener, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { localization } from "@web/core/l10n/localization";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { DateTimePickerPopover } from "@web/core/datetime/datetime_picker_popover";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

// Patching the core DateTimePicker logic to support hiding calendar
if (DateTimePicker.props && !DateTimePicker.props.showCalendar) {
    const showCalendarProp = { type: Boolean, optional: true };
    DateTimePicker.props.showCalendar = showCalendarProp;
    DateTimePicker.defaultProps.showCalendar = true;

    if (DateTimeInput.props) {
        DateTimeInput.props.showCalendar = showCalendarProp;
    }

    if (DateTimePickerPopover.props && DateTimePickerPopover.props.pickerProps) {
        DateTimePickerPopover.props.pickerProps.shape = DateTimePicker.props;
    }

    patch(DateTimePicker.prototype, {
        setup() {
            super.setup(...arguments);
            if (!this.props.showCalendar && (!this.props.value || (Array.isArray(this.props.value) && !this.props.value[0]))) {
                const now = DateTime.local();
                if (this.props.onSelect) {
                    Promise.resolve().then(() => {
                        if (this.props.onSelect) {
                            this.props.onSelect(now);
                        }
                    });
                }
            }
        }
    });
}

export class TimePickerField extends Component {
    static template = "advanced_alarms.TimePickerField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        super.setup(...arguments);
        this.is12HourFormat = localization.timeFormat.includes("h") || localization.timeFormat.includes("a");
        if (this.is12HourFormat) {
            this.hours = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0'));
        } else {
            this.hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'));
        }
        this.minutes = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'));
        this.state = useState({
            openDropdown: null,
        });
        this.rootRef = useRef("root");
        useExternalListener(window, "click", this.onWindowClick);
    }

    onWindowClick(ev) {
        if (this.rootRef.el && !this.rootRef.el.contains(ev.target)) {
            this.state.openDropdown = null;
        }
    }

    openDropdown(type) {
        this.state.openDropdown = type;
    }

    selectHour(h) {
        this.updateTime(h, this.currentMinute);
        this.state.openDropdown = null;
    }

    selectMinute(m) {
        this.updateTime(this.currentHour, m);
        this.state.openDropdown = null;
    }

    get parsedDate() {
        let val = this.props.record.data[this.props.name];
        if (!val) return null;
        if (typeof val === "string") {
            // Odoo 19 datetime fields might be passed as strings occasionally
            // In Odoo 19, we typically import deserializeDateTime, but since we don't have it explicitly imported here, 
            // we can parse it using luxon DateTime from UTC to Local.
            val = luxon.DateTime.fromSQL(val, { zone: "utc" }).setZone(luxon.Settings.defaultZone);
        }
        return val;
    }

    get currentHour() {
        const val = this.parsedDate;
        if (!val) return this.is12HourFormat ? "12" : "12";
        return val.toFormat(this.is12HourFormat ? "hh" : "HH");
    }

    get currentMinute() {
        const val = this.parsedDate;
        return val ? String(val.minute).padStart(2, '0') : "00";
    }

    get currentAmPm() {
        const val = this.parsedDate;
        if (!val) return "AM";
        return val.hour >= 12 ? "PM" : "AM";
    }

    toggleAmPm() {
        if (!this.is12HourFormat) return;
        const newAmPm = this.currentAmPm === "AM" ? "PM" : "AM";
        this.updateTime(this.currentHour, this.currentMinute, newAmPm);
    }

    onHourChange(ev) {
        this.updateTime(ev.target.value, this.currentMinute);
    }

    onMinuteChange(ev) {
        this.updateTime(this.currentHour, ev.target.value);
    }

    updateTime(hourStr, minuteStr, ampmStr) {
        let h = parseInt(hourStr, 10) || 0;
        const m = parseInt(minuteStr, 10) || 0;

        if (this.is12HourFormat) {
            const ampm = ampmStr || this.currentAmPm;
            if (ampm === "PM" && h !== 12) {
                h += 12;
            } else if (ampm === "AM" && h === 12) {
                h = 0;
            }
        }

        const baseDate = this.props.record.data[this.props.name] || DateTime.local();
        const updatedVal = baseDate.set({
            hour: h,
            minute: m,
            second: 0,
            millisecond: 0
        });
        
        this.props.record.update({ [this.props.name]: updatedVal });
    }

    get formattedTime() {
        const val = this.props.record.data[this.props.name];
        if (val) {
            return val.toFormat(localization.timeFormat);
        }
        return "";
    }
}

export const timePickerField = {
    component: TimePickerField,
    displayName: "Time Picker",
    supportedTypes: ["datetime"],
    isEmpty: (value) => value === false || value === null || value === "",
};

registry.category("fields").add("time_picker_widget", timePickerField);
