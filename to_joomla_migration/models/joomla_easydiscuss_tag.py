from odoo import models, fields


class EasyDiscussTag(models.TransientModel):
    _name = 'joomla.easydiscuss.tag'
    _description = 'EasyDiscuss Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'discuss_tags'

    name = fields.Char(joomla_column='title')
    odoo_id = fields.Many2one('forum.tag')

    def _prepare_forum_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            name=self.name,
            forum_id=self.migration_id.to_forum_id.id
        )
        return values

    def _get_matching_data(self, odoo_model):
        return self._get_matching_data_by_name(odoo_model)

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_forum_tag_values()
        tag = self.env['forum.tag'].create(values)
        return tag
