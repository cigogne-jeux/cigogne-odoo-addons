# Copyright 2023 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import ValidationError


class ScheduleTemplate(models.Model):
    _name = "schedule.template"
    _inherit = ["schedule.slot"]
    _description = "Schedule Template"

    template_id = fields.Many2one(comodel_name="schedule.template.type", required=True)


class ScheduleTemplateType(models.Model):
    _name = "schedule.template.type"
    _description = "Schedule Template Type"

    name = fields.Char()
    date = fields.Date()

    def plan(self):
        # this won't work well with localization where week start on sunday
        self.ensure_one()
        schedules = self.env["schedule.slot"]
        for template in self.env["schedule.template"].search(
            [("template_id", "=", self.id)]
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
                    "participant_ids": [(6, 0, template.participant_ids.ids)],
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
