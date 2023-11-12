import base64

import pytz
from icalendar import Calendar, Event

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import format_datetime


class ScheduleSendIcs(models.TransientModel):
    _name = "schedule.send.ics"
    _inherit = ["mail.thread"]
    _description = "Wizard: Send ics schedule"

    name = fields.Char(compute="_compute_name")
    contact_id = fields.Many2one(
        string="Contact",
        comodel_name="res.partner",
        default=lambda self: self.env.user.partner_id,
    )
    request_date_from = fields.Date()

    request_date_to = fields.Date()

    is_manager = fields.Boolean(
        string="are you a manager?", compute="_compute_is_manager"
    )
    request_datetime_from = fields.Datetime(compute="_compute_request_datetime_from")
    request_datetime_to = fields.Datetime(compute="_compute_request_datetime_to")

    @api.depends("contact_id", "request_date_from", "request_date_to")
    def _compute_name(self):
        for wizard in self:
            if (
                wizard.contact_id
                and wizard.request_date_from
                and wizard.request_date_to
            ):
                wizard.name = (
                    _("Schedule ")
                    + wizard.contact_id.name
                    + format_datetime(
                        self.env, wizard.request_datetime_from, dt_format=" dd.MM.YYYY"
                    )
                    + _(" to ")
                    + format_datetime(
                        self.env, wizard.request_datetime_to, dt_format="dd.MM.YYYY"
                    )
                )
            else:
                wizard.name = wizard.contact_id.name

    @api.depends("request_date_from")
    def _compute_request_datetime_from(self):
        for record in self:
            if record.request_date_from:
                record.request_datetime_from = fields.Datetime.to_datetime(
                    record.request_date_from
                )

    @api.depends("request_date_to")
    def _compute_request_datetime_to(self):
        for record in self:
            if record.request_date_to:
                datetime_to = fields.Datetime.to_datetime(record.request_date_to)
                datetime_to = fields.Datetime.add(datetime_to, hours=21, minutes=59)
                record.request_datetime_to = datetime_to

    @api.depends("contact_id")
    def _compute_is_manager(self):
        for record in self:
            if self.env.user.has_group("cigogne_planning.group_schedule_manager"):
                record.is_manager = True
            else:
                record.is_manager = False

    def send(self):
        self.ensure_one()
        slots = self.env["schedule.slot"].search(
            [
                ("start", ">=", self.request_date_from),
                ("start", "<=", self.request_date_to),
                ("participant_id", "=", self.contact_id.id),
            ]
        )
        if not slots:
            raise UserError(_("No schedule to send"))
        slots = slots.sorted(key=lambda r: r.start)
        cal = self.create_ics(slots).to_ical()
        att_ics_id = self.env["ir.attachment"].create(
            {
                "name": self.name + ".ics",
                "type": "binary",
                "datas": base64.encodestring(cal),
                "res_model": "schedule.send.ics",
                "res_id": self.id,
                "mimetype": "text/calendar",
            }
        )
        ctx = dict(
            default_model="schedule.send.ics",
            default_res_id=self.id,
            default_body="Planning",
            default_email_from='"La Cigogne" <info@cigogne-jeux.ch>',
            default_author_id=False,
            default_subject=self.name,
            default_partner_ids=self.contact_id.ids,
            default_composition_mode="mass_mail",
            default_attachment_ids=att_ics_id.ids,
        )
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "target": "new",
            "context": ctx,
        }

    def create_ics(self, slots):
        cal = Calendar()
        base_url = self.sudo().env["ir.config_parameter"].get_param("web.base.url")
        for slot in slots:
            e = Event()
            e.add("uid", slot.id)
            e.add("summary", slot.name)
            e.add("dtstart", pytz.utc.localize(slot.start))
            e.add("dtend", pytz.utc.localize(slot.end))
            url = base_url + "/web#id=%d&view_type=form&model=%s" % (
                slot.id,
                slot._name,
            )
            e.add("url", url)
            if slot.comment:
                e.add("description", slot.comment)
            e.add("status", "CONFIRMED")
            cal.add_component(e)
        return cal
