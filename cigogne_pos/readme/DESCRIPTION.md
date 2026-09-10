Odoo 18 records an opening cash difference in the point of sale session chatter,
but does not create the corresponding accounting entry.

This module restores the accounting correction for future sessions. Opening cash
gains and losses are posted in the cash journal against its configured profit or
loss account.

The correction is linked to the session for audit purposes and appears in its
related journal items. It is not linked as a session cash movement, which prevents
Odoo 18 from including it again in the theoretical closing balance.
