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
import { Component } from "@odoo/owl";
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

    get timeValue() {
        const val = this.props.record.data[this.props.name];
        if (val) {
            return val.toFormat("HH:mm");
        }
        return "12:00";
    }

    onTimeChange(ev) {
        const timeStr = ev.target.value; // e.g. "14:30"
        if (!timeStr) return;

        const [hours, minutes] = timeStr.split(':').map(Number);
        const baseDate = this.props.record.data[this.props.name] || DateTime.local();
        
        const updatedVal = baseDate.set({
            hour: hours,
            minute: minutes,
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
