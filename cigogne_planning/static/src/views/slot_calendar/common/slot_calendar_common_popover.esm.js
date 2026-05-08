import {CalendarCommonPopover} from "@web/views/calendar/calendar_common/calendar_common_popover";
import {user} from "@web/core/user";

export class SlotCalendarCommonPopover extends CalendarCommonPopover {
    get canParticipate() {
        return this.props.record.rawRecord.state === "available";
    }

    get canQuit() {
        return user.partnerId === this.props.record.rawRecord.participant_id[0];
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

SlotCalendarCommonPopover.subTemplates = {
    ...CalendarCommonPopover.subTemplates,
    footer: "cigogne_planning.SlotCalendarCommonPopover.footer",
};
