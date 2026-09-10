# Copyright 2026 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    opening_pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="Opening POS Session",
        index=True,
        ondelete="set null",
    )
