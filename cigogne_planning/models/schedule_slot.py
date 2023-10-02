# Copyright 2023 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
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
    participant_ids = fields.Many2many(
        string="Participants",
        comodel_name="res.partner",
        domain=[("user_ids", "!=", False)],
    )
    is_participant = fields.Boolean(
        compute="_compute_is_participant",
        search="_search_is_participant",
    )
    capacity = fields.Integer()
    state = fields.Selection(
        selection=[
            ("available", "Available"),
            ("full", "Full"),
        ],
        compute="_compute_state",
    )
    comment = fields.Text()

    def name_get(self):
        res = []
        for slot in self:
            if slot.name and slot.start and slot.end:
                name = (
                    slot.name
                    + format_datetime(self.env, slot.start, dt_format=" HH:mm-")
                    + format_datetime(self.env, slot.end, dt_format="HH:mm dd.MM.YYYY")
                )
                res.append((slot.id, name))
            else:
                super().name_get()
        return res

    @api.constrains("participant_ids", "capacity")
    def _check_participants_capacity(self):
        for slot in self:
            if len(slot.participant_ids) > slot.capacity:
                raise ValidationError(
                    _("The number of participants cannot be greater than the capacity")
                )

    def _compute_state(self):
        for slot in self:
            slot.state = (
                "full" if len(slot.participant_ids) == slot.capacity else "available"
            )

    def _compute_is_participant(self):
        for slot in self:
            slot.is_participant = (
                True if self.env.user.partner_id in slot.participant_ids else False
            )

    @api.model
    def _search_is_participant(self, operator, operand):
        # Cases ('is_participant', '=', True) or  ('is_participant', '!=', False)
        if (operator == "=" and operand) or (operator == "!=" and not operand):
            return [("participant_ids", "in", self.env.user.partner_id.ids)]
        else:
            return [("participant_ids", "not in", self.env.user.partner_id.ids)]

    def participate(self):
        for slot in self.sudo():
            slot.participant_ids += self.env.user.partner_id

    def quit(self):
        for slot in self.sudo():
            slot.participant_ids -= self.env.user.partner_id

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super()._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get("participant_ids"):
            for partnerid in updated_values["participant_ids"][0][2]:
                res.append((partnerid, subtype_ids, False))
        return res
