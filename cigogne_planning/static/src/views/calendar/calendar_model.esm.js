import {CalendarModel} from "@web/views/calendar/calendar_model";
import {patch} from "@web/core/utils/patch";

patch(CalendarModel.prototype, {
    makeFilterAll(previousAllFilter, isUserOrPartner, sectionLabel) {
        const result = super.makeFilterAll(
            previousAllFilter,
            isUserOrPartner,
            sectionLabel
        );
        result.active = previousAllFilter ? previousAllFilter.active : true;
        return result;
    },
});
