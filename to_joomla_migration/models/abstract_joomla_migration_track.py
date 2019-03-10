from odoo import fields, models


class AbstractJoomlaMigrationTrack(models.AbstractModel):
    _inherit = 'abstract.joomla.migration.track'

    # Odoo does not allow relation with a transient model, so we use an Integer field here alternatively
    migration_id = fields.Integer(string='Migration Wizard ID',
                                   help="Technical field to map the record with Migration Wizard record temporarily")
