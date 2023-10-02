# Copyright 2023 La cigogne - Bar à jeux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Planning",
    "summary": "Manage planning schedules in a cooperative way",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Uncategorized",
    "website": "https://github.com/cigogne-jeux/cigogne-odoo-addons",
    "author": "La Cigogne - Bar à jeux",
    "maintainers": ["jguenat", "i0np"],
    "license": "AGPL-3",
    "depends": [
        "mail",
    ],
    "data": [
        "security/planning_security.xml",
        "security/ir.model.access.csv",
        "views/schedule_slot_view.xml",
        "views/schedule_template_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cigogne_planning/static/src/css/calendar.css",
        ],
    },
}
