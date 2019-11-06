from odoo import fields, models


class AbstractJoomlaMigrationTrack(models.AbstractModel):
    _name = 'abstract.joomla.migration.track'
    _description = 'Abstract Joomla Migration Track'

    old_website = fields.Char()
    old_website_model = fields.Char()
    old_website_record_id = fields.Integer()
