import {CalendarRenderer} from "@web/views/calendar/calendar_renderer";
import {SlotCalendarCommonRenderer} from "@cigogne_planning/views/slot_calendar/common/slot_calendar_common_renderer.esm";
import {SlotCalendarMonthCommonRenderer} from "@cigogne_planning/views/slot_calendar/common/slot_calendar_month_common_renderer.esm";

export class SlotCalendarRenderer extends CalendarRenderer {}
SlotCalendarRenderer.components = {
    ...CalendarRenderer.components,
    day: SlotCalendarCommonRenderer,
    week: SlotCalendarCommonRenderer,
    month: SlotCalendarMonthCommonRenderer,
};
