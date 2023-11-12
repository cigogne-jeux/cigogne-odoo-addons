# Copyright 2023 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import format_datetime


class ScheduleSlot(models.Model):
    _name = "schedule.slot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _mail_post_access = "read"
    _description = "Schedule"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    start = fields.Datetime(required=True, tracking=True)
    end = fields.Datetime(required=True, tracking=True)
    allday = fields.Boolean("All Day")
    user_id = fields.Many2one(
        string="Organizer",
        comodel_name="res.users",
        default=lambda self: self.env.user,
    )
    participant_id = fields.Many2one(
        string="Participant",
        comodel_name="res.partner",
        domain=[("user_ids", "!=", False)],
    )
    participant_ids = fields.Many2many(
        string="Participants",
        comodel_name="res.partner",
        domain=[("user_ids", "!=", False)],
    )
    is_participant = fields.Boolean(
        compute="_compute_is_participant",
        search="_search_is_participant",
    )
    state = fields.Selection(
        selection=[
            ("available", "Available"),
            ("full", "Full"),
        ],
        compute="_compute_state",
        store=True,
    )
    type_id = fields.Many2one(
        comodel_name="schedule.template.type",
        required=True,
    )
    comment = fields.Text()

    def name_get(self):
        res = []
        for slot in self:
            if slot.name and slot.start and slot.end:
                name = (
                    slot.name
                    + format_datetime(self.env, slot.start, dt_format=" HH:mm-")
                    + format_datetime(self.env, slot.end, dt_format="HH:mm")
                    + " "
                    + format_datetime(self.env, slot.start, dt_format="dd.MM.YYYY")
                    + " "
                    + (slot.participant_id.name if slot.participant_id else "")
                )
                res.append((slot.id, name))
            else:
                super().name_get()
        return res

    @api.depends("participant_id")
    def _compute_state(self):
        for slot in self:
            slot.state = "full" if slot.participant_id else "available"

    def _compute_is_participant(self):
        for slot in self:
            slot.is_participant = (
                True if self.env.user.partner_id == slot.participant_id else False
            )

    @api.model
    def _search_is_participant(self, operator, operand):
        # Cases ('is_participant', '=', True) or  ('is_participant', '!=', False)
        if (operator == "=" and operand) or (operator == "!=" and not operand):
            return [("participant_id", "in", self.env.user.partner_id.ids)]
        else:
            return [("participant_id", "not in", self.env.user.partner_id.ids)]

    def participate(self):
        for slot in self.sudo():
            slot.participant_id = self.env.user.partner_id

    def quit(self):
        for slot in self.sudo():
            if not slot.is_participant:
                raise UserError(_("You can only quit your own schedule."))
            if (
                slot.type_id.deadline
                <= (fields.Date.to_date(slot.start.date()) - fields.Date.today()).days
            ):
                slot.participant_id = False
            else:
                raise UserError(
                    _(
                        "It's no longer possible to quit this schedule (deadline reached)."
                    )
                )

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super()._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get("participant_id"):
            res.append((updated_values["participant_id"], subtype_ids, False))
        return res
