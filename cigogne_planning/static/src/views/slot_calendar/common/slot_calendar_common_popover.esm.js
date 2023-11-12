/** @odoo-module **/

import {CalendarCommonPopover} from "@web/views/calendar/calendar_common/calendar_common_popover";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {useService} from "@web/core/utils/hooks";

export class SlotCalendarCommonPopover extends CalendarCommonPopover {
    setup() {
        super.setup();
        this.user = useService("user");
        this.orm = useService("orm");
    }

    get canParticipate() {
        return this.props.record.rawRecord.state === "available";
    }

    get canQuit() {
        return (
            this.env.services.user.partnerId ===
            this.props.record.rawRecord.participant_id[0]
        );
    }

    async onClickParticipate() {
        const record = this.props.record;
        await this.env.services.orm.call(this.props.model.resModel, "participate", [
            [record.id],
        ]);
        await this.props.model.load();
        this.props.close();
    }

    async onClickQuit() {
        const record = this.props.record;
        await this.env.services.orm.call(this.props.model.resModel, "quit", [
            [record.id],
        ]);
        await this.props.model.load();
        this.props.close();
    }
}
SlotCalendarCommonPopover.components = {
    ...CalendarCommonPopover.components,
    Dropdown,
    DropdownItem,
};
SlotCalendarCommonPopover.subTemplates = {
    ...CalendarCommonPopover.subTemplates,
    footer: "cigogne_planning.SlotCalendarCommonPopover.footer",
};
