/** @odoo-module **/

import {CalendarModel} from "@web/views/calendar/calendar_model";
import {patch} from "@web/core/utils/patch";

patch(CalendarModel.prototype, "CigogneCalendarModel", {
    makeFilterAll(previousAllFilter) {
        const filters = this._super(...arguments);
        filters.active = previousAllFilter ? previousAllFilter.active : true;
        return filters;
    },
});
