import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_easydiscuss = fields.Boolean(default=False)
    easydiscuss_post_ids = fields.One2many('joomla.easydiscuss.post', 'migration_id')
    easydiscuss_tag_ids = fields.One2many('joomla.easydiscuss.tag', 'migration_id')
    easydiscuss_attachment_ids = fields.One2many('joomla.easydiscuss.attachment', 'migration_id')
    easydiscuss_vote_ids = fields.One2many('joomla.easydiscuss.vote', 'migration_id')
    easydicuss_comment_ids = fields.One2many('joomla.easydiscuss.comment', 'migration_id')

    def get_joomla_models(self):
        jmodels = super(JoomlaMigration, self).get_joomla_models()
        if self.include_easydiscuss:
            for model in ['joomla.easydiscuss.post', 'joomla.easydiscuss.category',
                          'joomla.easydiscuss.tag', 'joomla.easydiscuss.post.tag',
                          'joomla.easydiscuss.attachment', 'joomla.easydiscuss.vote', 'joomla.easydiscuss.comment']:
                jmodels[model] = 400
        return jmodels

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_easydiscuss:
            self._migrate_easydiscuss()

    def _migrate_easydiscuss(self):
        self.easydiscuss_tag_ids.migrate_to_forum_tag()
        self.easydiscuss_attachment_ids.migrate_to_ir_attachment()
        self.easydiscuss_post_ids.migrate_to_forum_post()
        self.easydiscuss_vote_ids.migrate_to_forum_post_vote()
        self.easydicuss_comment_ids.migrate_to_forum_post_comment()
        self.easydiscuss_post_ids.update_write_date()

    def _get_records_to_reset(self):
        res = super(JoomlaMigration, self)._get_records_to_reset()
        posts = self.env['forum.post'].get_migrated_data()
        tags = self.env['forum.tag'].get_migrated_data()
        res.extend([(posts, 500), (tags, 525)])
        return res
