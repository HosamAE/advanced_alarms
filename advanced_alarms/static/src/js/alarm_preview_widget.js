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
import { Component, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { localization } from "@web/core/l10n/localization";

const { DateTime } = luxon;

export class AlarmPreviewField extends Component {
    static template = "advanced_alarms.AlarmPreviewField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.previewDays = this.calculatePreviewDays(this.props.record);
        onWillUpdateProps((nextProps) => {
            this.previewDays = this.calculatePreviewDays(nextProps.record);
        });
    }

    calculatePreviewDays(record) {
        const days = [];
        let currentDt = DateTime.local();
        
        const data = record.data;
        const recurrence = data.recurrence_type;
        
        let alarmTimeStr = "--:--";
        if (data.alarm_time) {
            alarmTimeStr = data.alarm_time.toFormat(localization.timeFormat);
        }
        
        if (data.intraday_repeat && data.intraday_interval > 0) {
            const uomStr = data.intraday_uom === 'hours' ? 'hr' : 'm';
            alarmTimeStr = `${alarmTimeStr} (+Every ${data.intraday_interval}${uomStr})`;
        }

        for (let i = 0; i < 4; i++) {
            const targetDt = currentDt.plus({ days: i });
            let isActive = false;
            
            if (recurrence === 'once') {
                isActive = (i === 0);
            } else if (recurrence === 'scrum') {
                const wd = targetDt.weekday;
                isActive = ([1, 2, 3, 4, 7].includes(wd));
            } else if (recurrence === 'custom') {
                const wd = targetDt.weekday;
                const map = {
                    1: data.recur_mon,
                    2: data.recur_tue,
                    3: data.recur_wed,
                    4: data.recur_thu,
                    5: data.recur_fri,
                    6: data.recur_sat,
                    7: data.recur_sun
                };
                isActive = map[wd];
            } else if (recurrence === 'shift') {
                if (data.shift_start_date && data.shift_work_days > 0) {
                    const startDt = DateTime.fromISO(data.shift_start_date.toISODate());
                    const diffDays = Math.floor(targetDt.diff(startDt, 'days').days);
                    const cycle = data.shift_work_days + data.shift_off_days;
                    if (cycle > 0 && diffDays >= 0) {
                        const mod = diffDays % cycle;
                        isActive = (mod < data.shift_work_days);
                    }
                }
            } else if (recurrence === 'cycle') {
                // Approximate for frontend: assume active since they configure the cycle days manually
                isActive = true;
                alarmTimeStr = "Cycle Mode";
            }

            days.push({
                index: i,
                label: i === 0 ? "Today" : `Day ${i + 1}`,
                dateStr: targetDt.toFormat("MMM dd"),
                time: alarmTimeStr,
                isActive: isActive
            });
        }
        
        return days;
    }
}

export const alarmPreviewField = {
    component: AlarmPreviewField,
    supportedTypes: ["char"], // Dummy field
};

registry.category("fields").add("alarm_preview", alarmPreviewField);
