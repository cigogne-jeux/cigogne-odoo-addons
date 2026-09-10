# Copyright 2026 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@tagged("post_install", "-at_install")
class TestPosOpeningCashDifference(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config.cash_control = True
        cls.cash_journal = cls.pos_config.payment_method_ids.filtered("is_cash_count")[
            :1
        ].journal_id
        cls.profit_account = cls.env["account.account"].create(
            {
                "name": "POS Cash Difference Profit",
                "code": "POSDIFFGAIN",
                "account_type": "income_other",
            }
        )
        cls.loss_account = cls.env["account.account"].create(
            {
                "name": "POS Cash Difference Loss",
                "code": "POSDIFFLOSS",
                "account_type": "expense",
            }
        )
        cls.cash_journal.write(
            {
                "profit_account_id": cls.profit_account.id,
                "loss_account_id": cls.loss_account.id,
            }
        )

    def _open_session(self, expected_cash, counted_cash):
        session = self.env["pos.session"].create(
            {
                "config_id": self.pos_config.id,
                "user_id": self.env.user.id,
            }
        )
        self.assertEqual(session.state, "opening_control")
        self.assertEqual(session.cash_journal_id, self.cash_journal)
        session.cash_register_balance_start = expected_cash
        session.set_opening_control(counted_cash, None)
        return session

    def _get_opening_difference_line(self):
        return self.env["account.bank.statement.line"].search(
            [
                ("journal_id", "=", self.cash_journal.id),
                ("payment_ref", "ilike", "opening"),
            ]
        )

    def test_opening_cash_gain_posts_profit(self):
        session = self._open_session(100.0, 125.0)

        statement_line = self._get_opening_difference_line()
        self.assertEqual(statement_line.amount, 25.0)
        self.assertFalse(statement_line.pos_session_id)
        self.assertEqual(statement_line.opening_pos_session_id, session)
        self.assertFalse(session.statement_line_ids)
        self.assertIn(statement_line.move_id, session._get_related_account_moves())
        self.assertEqual(statement_line.move_id.state, "posted")
        self.assertIn(
            f'data-oe-id="{session.id}"',
            " ".join(statement_line.move_id.message_ids.mapped("body")),
        )
        self.assertRecordValues(
            statement_line.move_id.line_ids,
            [
                {
                    "balance": 25.0,
                    "account_id": self.cash_journal.default_account_id.id,
                },
                {"balance": -25.0, "account_id": self.profit_account.id},
            ],
        )

    def test_opening_cash_loss_posts_loss(self):
        self._open_session(100.0, 90.0)

        statement_line = self._get_opening_difference_line()
        self.assertEqual(statement_line.amount, -10.0)
        self.assertFalse(statement_line.pos_session_id)
        self.assertRecordValues(
            statement_line.move_id.line_ids,
            [
                {
                    "balance": -10.0,
                    "account_id": self.cash_journal.default_account_id.id,
                },
                {"balance": 10.0, "account_id": self.loss_account.id},
            ],
        )

    def test_zero_difference_and_repeated_opening_do_not_post(self):
        session = self._open_session(100.0, 100.0)
        session.set_opening_control(125.0, None)

        self.assertFalse(self._get_opening_difference_line())

    def test_missing_profit_account_blocks_opening(self):
        self.cash_journal.write({"profit_account_id": False})
        self.env.invalidate_all()
        self.assertFalse(self.cash_journal.profit_account_id)

        with self.assertRaises(UserError):
            self._open_session(100.0, 125.0)

    def test_opening_difference_is_not_counted_again_at_closing(self):
        session = self._open_session(100.0, 90.0)
        session.post_closing_cash_details(90.0)
        session.close_session_from_ui()

        self.assertEqual(session.cash_register_difference, 0.0)
        self.assertEqual(len(self._get_opening_difference_line()), 1)
        self.assertFalse(
            self.env["account.bank.statement.line"].search(
                [
                    ("journal_id", "=", self.cash_journal.id),
                    ("payment_ref", "ilike", "closing"),
                ]
            )
        )
