/** @odoo-module **/

import {SlotCalendarRenderer} from "@cigogne_planning/views/slot_calendar/slot_calendar_renderer.esm";
import {calendarView} from "@web/views/calendar/calendar_view";
import {registry} from "@web/core/registry";

export const slotCalendarView = {
    ...calendarView,
    Renderer: SlotCalendarRenderer,
};

registry.category("views").add("slot_calendar", slotCalendarView);
