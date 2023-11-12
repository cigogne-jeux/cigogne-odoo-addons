# Copyright 2023 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ScheduleTemplate(models.Model):
    _name = "schedule.template"
    _inherit = ["schedule.slot"]
    _description = "Schedule Template"


class ScheduleTemplateType(models.Model):
    _name = "schedule.template.type"
    _description = "Schedule Template Type"

    name = fields.Char()
    deadline = fields.Integer(
        help="Deadline (in days) before shedule when it is still possible to quit"
    )
    date = fields.Date()

    def plan(self):
        # this won't work well with localization where week start on sunday
        self.ensure_one()
        if not self.date:
            raise ValidationError(_("No date defined."))
        schedules = self.env["schedule.slot"]
        for template in self.env["schedule.template"].search(
            [("type_id", "=", self.id)]
        ):
            plandate = self.date + relativedelta(
                days=template.start.date().weekday() - self.date.weekday()
            )
            plandate_start = template.start.replace(
                year=plandate.year, month=plandate.month, day=plandate.day
            )
            start_cor_tz = self.correct_tz(template.start, plandate_start)

            plandate = self.date + relativedelta(
                days=template.end.date().weekday() - self.date.weekday()
            )
            plandate_end = template.end.replace(
                year=plandate.year, month=plandate.month, day=plandate.day
            )
            end_cor_tz = self.correct_tz(template.end, plandate_end)

            schedule = self.env["schedule.slot"].create(
                {
                    "name": template.name,
                    "start": start_cor_tz,
                    "end": end_cor_tz,
                    "allday": template.allday,
                    "comment": template.comment,
                    "type_id": template.type_id.id,
                    "participant_id": template.participant_id.id,
                }
            )
            schedules |= schedule
        return schedules

    def correct_tz(self, refdate, datecheck):
        if not self.env.user.tz:
            raise ValidationError(
                self.env.user.name + " n'a pas de fuseau horaire définit"
            )
        USERTZ = pytz.timezone(self.env.user.tz)
        UTC = pytz.utc
        refdatedtz = (
            UTC.localize(refdate) - USERTZ.localize(refdate).astimezone(UTC)
        ).seconds / 3600
        datecheckdtz = (
            UTC.localize(datecheck) - USERTZ.localize(datecheck).astimezone(UTC)
        ).seconds / 3600
        if datecheckdtz != refdatedtz:
            deltatzdiff = refdatedtz - datecheckdtz
            corrdate = datecheck + relativedelta(hours=deltatzdiff)
            return corrdate
        else:
            return datecheck
