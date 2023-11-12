from openupgradelib import openupgrade


def participants_to_participant(env):
    # Move data from participant_ids to participant_id
    slots = env["schedule.slot"].search([])
    for slot in slots:
        if slot.participant_ids:
            slot.participant_id = slot.participant_ids[0]


@openupgrade.migrate()
def migrate(env, version):
    participants_to_participant(env)
