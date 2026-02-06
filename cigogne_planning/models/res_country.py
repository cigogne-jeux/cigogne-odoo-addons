# Copyright 2026 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    active = fields.Boolean(default=True)
