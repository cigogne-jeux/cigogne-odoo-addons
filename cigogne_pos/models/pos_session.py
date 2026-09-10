# Copyright 2026 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import _, fields, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _set_opening_control_data(self, cashbox_value: int, notes: str):
        expected_cash = self.cash_register_balance_start
        result = super()._set_opening_control_data(cashbox_value, notes)
        difference = cashbox_value - expected_cash
        if self.cash_journal_id and not self.currency_id.is_zero(difference):
            self.sudo()._post_opening_cash_difference(difference)
        return result

    def _post_opening_cash_difference(self, amount):
        self.ensure_one()
        if amount < 0.0:
            counterpart_account = self.cash_journal_id.loss_account_id
            if not counterpart_account:
                raise UserError(
                    _(
                        "Please go on the %s journal and define a Loss Account. "
                        "This account will be used to record cash difference.",
                        self.cash_journal_id.name,
                    )
                )
            payment_ref = _(
                "Cash difference observed during the counting (Loss) - opening"
            )
        else:
            counterpart_account = self.cash_journal_id.profit_account_id
            if not counterpart_account:
                raise UserError(
                    _(
                        "Please go on the %s journal and define a Profit Account. "
                        "This account will be used to record cash difference.",
                        self.cash_journal_id.name,
                    )
                )
            payment_ref = _(
                "Cash difference observed during the counting (Profit) - opening"
            )

        date = fields.Date.context_today(self)
        statement_line_values = {
            "journal_id": self.cash_journal_id.id,
            "amount": amount,
            "date": date,
            "payment_ref": payment_ref,
            "opening_pos_session_id": self.id,
        }
        if counterpart_account.tax_ids:
            statement_line_values["line_ids"] = self._prepare_cash_diff_line_ids(
                amount,
                counterpart_account,
                counterpart_account.tax_ids,
                payment_ref,
                date,
            )
        else:
            statement_line_values["counterpart_account_id"] = counterpart_account.id

        statement_line = self.env["account.bank.statement.line"].create(
            statement_line_values
        )
        statement_line.move_id.message_post(
            body=_("Related Session: %(link)s", link=self._get_html_link())
        )

    def _get_other_related_moves(self):
        related_moves = super()._get_other_related_moves()
        opening_difference_moves = (
            self.env["account.bank.statement.line"]
            .search([("opening_pos_session_id", "in", self.ids)])
            .move_id
        )
        return related_moves | opening_difference_moves
