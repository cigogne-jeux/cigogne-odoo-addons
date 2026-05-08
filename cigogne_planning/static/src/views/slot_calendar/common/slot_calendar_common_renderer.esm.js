import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {SlotCalendarCommonPopover} from "@cigogne_planning/views/slot_calendar/common/slot_calendar_common_popover.esm";
import {renderToString} from "@web/core/utils/render";

export class SlotCalendarCommonRenderer extends CalendarCommonRenderer {
    /**
     * @override
     */
    get options() {
        return Object.assign(super.options, {
            slotEventOverlap: false,
        });
    }
    onEventContent(arg) {
        // Rewrite to add custom field participant
        const {event} = arg;
        if (event.start && event.end) {
            const dateFmt = (date) =>
                luxon.DateTime.fromJSDate(date).toFormat(this.timeFormat);
            arg.timeText = `${dateFmt(event.start)} - ${dateFmt(event.end)}`;
        }
        const record = this.props.model.records[event.id];
        if (record) {
            // This is needed in order to give the possibility to change the event template.
            const injectedContentStr = renderToString(this.constructor.eventTemplate, {
                ...record,
                startTime: this.getStartTime(record),
                endTime: this.getEndTime(record),
                participant: record.rawRecord.participant_id[1],
            });
            const domParser = new DOMParser();
            const {children} = domParser.parseFromString(
                injectedContentStr,
                "text/html"
            ).body;
            return {domNodes: children};
        }
        return true;
    }
}

SlotCalendarCommonRenderer.eventTemplate =
    "cigogne_planning.SlotCalendarCommonRenderer.slot";
SlotCalendarCommonRenderer.components = {
    ...CalendarCommonRenderer.components,
    Popover: SlotCalendarCommonPopover,
};
