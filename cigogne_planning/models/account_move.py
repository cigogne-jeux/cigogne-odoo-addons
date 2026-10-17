from odoo import api, models

from odoo.addons.account.models.account_move import AccountMove as AccountMoveBase


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _routing_check_route(self, message, message_dict, route, raise_exception=True):
        """Restore importing invoice with no attachment in email alias."""
        if (
            route[0] == "account.move"
            and len(message_dict.get("attachments") or []) < 1
        ):
            return super(AccountMoveBase, self)._routing_check_route(
                message,
                message_dict,
                route,
                raise_exception=raise_exception,
            )
        return super()._routing_check_route(
            message,
            message_dict,
            route,
            raise_exception=raise_exception,
        )
