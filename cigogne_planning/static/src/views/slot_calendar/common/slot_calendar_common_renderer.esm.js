/** @odoo-module **/

import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {SlotCalendarCommonPopover} from "@cigogne_planning/views/slot_calendar/common/slot_calendar_common_popover.esm";
import {getColor} from "@web/views/calendar/colors";
import {patch} from "@web/core/utils/patch";
import {renderToString} from "@web/core/utils/render";

patch(CalendarCommonRenderer.prototype, "CigognePlanningCommonRenderer", {
    get options() {
        const options = this._super(...arguments);
        options.slotEventOverlap = false;
        return options;
    },
});

export class SlotCalendarCommonRenderer extends CalendarCommonRenderer {
    /**
     * @override
     */
    onEventRender(info) {
        const {el, event} = info;
        el.dataset.eventId = event.id;
        el.classList.add("o_event", "py-0");
        const record = this.props.model.records[event.id];

        if (record) {
            // This is needed in order to give the possibility to change the event template.
            const injectedContentStr = renderToString(this.constructor.eventTemplate, {
                ...record,
                startTime: this.getStartTime(record),
                endHourLocated: record.rawRecord.end_hour_located,
                participant: record.rawRecord.participant_id[1],
            });
            const domParser = new DOMParser();
            const {children} = domParser.parseFromString(
                injectedContentStr,
                "text/html"
            ).body;
            el.querySelector(".fc-content").replaceWith(...children);

            const color = getColor(record.colorIndex);
            if (typeof color === "string") {
                el.style.backgroundColor = color;
            } else if (typeof color === "number") {
                el.classList.add(`o_calendar_color_${color}`);
            } else {
                el.classList.add("o_calendar_color_0");
            }

            if (record.isHatched) {
                el.classList.add("o_event_hatched");
            }
            if (record.isStriked) {
                el.classList.add("o_event_striked");
            }
        }

        if (!el.querySelector(".fc-bg")) {
            const bg = document.createElement("div");
            bg.classList.add("fc-bg");
            el.appendChild(bg);
        }
    }
}

SlotCalendarCommonRenderer.eventTemplate =
    "cigogne_planning.SlotCalendarCommonRenderer.slot";
SlotCalendarCommonRenderer.components = {
    ...CalendarCommonRenderer.components,
    Popover: SlotCalendarCommonPopover,
};
