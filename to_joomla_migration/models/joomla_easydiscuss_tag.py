import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class EasyDiscussTag(models.TransientModel):
    _name = 'joomla.easydiscuss.tag'
    _description = 'EasyDiscuss Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'discuss_tags'

    name = fields.Char(joomla_column='title')
    forum_tag_id = fields.Many2one('forum.tag')

    def _prepare_forum_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            name=self.name,
            forum_id=self.migration_id.to_forum_id.id
        )
        return values

    def migrate_to_forum_tag(self):
        tags = self.env['forum.tag'].search([])
        tag_names = {r.name: r for r in tags}
        for idx, jtag in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating easydiscuss tag {}'.format(idx, len(self), jtag.name))
            tag = tag_names.get(jtag.name)
            if not tag:
                values = jtag._prepare_forum_tag_values()
                tag = tags.create(values)
            jtag.forum_tag_id = tag
