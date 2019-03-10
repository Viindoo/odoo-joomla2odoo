from odoo import fields, models


class AbstractJoomlaMigrationTrack(models.AbstractModel):
    _name = 'abstract.joomla.migration.track'

    old_website = fields.Char()
    old_website_model = fields.Char()
    old_website_record_id = fields.Integer()
