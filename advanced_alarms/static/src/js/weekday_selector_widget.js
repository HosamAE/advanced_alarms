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
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { localization } from "@web/core/l10n/localization";

export class WeekdaySelectorField extends Component {
    static template = "advanced_alarms.WeekdaySelectorField";
    static props = {
        "*": true,
    };

    get days() {
        const record = this.props.record.data;
        const allDays = [
            { key: 'recur_sun', label: 'S', active: record.recur_sun }, // 7 (Sunday)
            { key: 'recur_mon', label: 'M', active: record.recur_mon }, // 1 (Monday)
            { key: 'recur_tue', label: 'T', active: record.recur_tue }, // 2
            { key: 'recur_wed', label: 'W', active: record.recur_wed }, // 3
            { key: 'recur_thu', label: 'T', active: record.recur_thu }, // 4
            { key: 'recur_fri', label: 'F', active: record.recur_fri }, // 5
            { key: 'recur_sat', label: 'S', active: record.recur_sat }, // 6
        ];
        
        // Odoo weekStart: 1 = Monday, 7 = Sunday
        const weekStart = localization.weekStart || 7;
        
        // If weekStart is 7 (Sunday), we don't need to shift.
        // If weekStart is 1 (Monday), we shift Sunday to the end.
        if (weekStart === 1) {
            const sunday = allDays.shift();
            allDays.push(sunday);
        } else if (weekStart !== 7) {
            // General case for other week starts (e.g. 6 = Saturday in some Arab countries)
            // Array index 0 is Sunday. So if weekStart is 6 (Saturday), shift index 6 to start.
            // Map weekStart (1=Mon..7=Sun) to our array index (0=Sun..6=Sat)
            const startIndex = weekStart === 7 ? 0 : weekStart;
            return allDays.slice(startIndex).concat(allDays.slice(0, startIndex));
        }
        
        return allDays;
    }

    async toggleDay(dayKey) {
        if (this.props.readonly) return;
        const record = this.props.record;
        const currentValue = record.data[dayKey];
        await record.update({ [dayKey]: !currentValue });
    }
}

registry.category("fields").add("weekday_selector", {
    component: WeekdaySelectorField,
    supportedTypes: ["boolean"],
});
