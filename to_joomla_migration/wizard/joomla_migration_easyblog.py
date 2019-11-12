import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_easyblog = fields.Boolean(default=False)
    easyblog_post_ids = fields.One2many('joomla.easyblog.post', 'migration_id')
    easyblog_tag_ids = fields.One2many('joomla.easyblog.tag', 'migration_id')

    def get_joomla_models(self):
        jmodels = super(JoomlaMigration, self).get_joomla_models()
        if self.include_easyblog:
            for model in ['joomla.easyblog.post', 'joomla.easyblog.meta', 'joomla.easyblog.tag', 'joomla.easyblog.post.tag', 'joomla.menu']:
                jmodels[model] = 300
        return jmodels

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_easyblog:
            self._migrate_easyblog()

    def _migrate_easyblog(self):
        self.easyblog_tag_ids.migrate_to_blog_tag()
        self.easyblog_post_ids.migrate_to_blog_post()
