/** @odoo-module **/

import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {SlotCalendarCommonPopover} from "@cigogne_planning/views/slot_calendar/common/slot_calendar_common_popover.esm";

export class SlotCalendarMonthCommonRenderer extends CalendarCommonRenderer {}

SlotCalendarMonthCommonRenderer.components = {
    ...CalendarCommonRenderer.components,
    Popover: SlotCalendarCommonPopover,
};
