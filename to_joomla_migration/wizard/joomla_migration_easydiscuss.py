from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_easydiscuss = fields.Boolean(default=False)
    easydiscuss_post_ids = fields.One2many('joomla.easydiscuss.post', 'migration_id')
    easydiscuss_tag_ids = fields.One2many('joomla.easydiscuss.tag', 'migration_id')
    easydiscuss_attachment_ids = fields.One2many('joomla.easydiscuss.attachment', 'migration_id')
    easydiscuss_vote_ids = fields.One2many('joomla.easydiscuss.vote', 'migration_id')
    easydicuss_comment_ids = fields.One2many('joomla.easydiscuss.comment', 'migration_id')

    def _get_joomla_models(self):
        jmodels = super(JoomlaMigration, self)._get_joomla_models()
        if self.include_easydiscuss:
            for model in ['joomla.easydiscuss.post', 'joomla.easydiscuss.category', 'joomla.easydiscuss.tag',
                          'joomla.easydiscuss.attachment', 'joomla.easydiscuss.vote', 'joomla.easydiscuss.comment']:
                jmodels[model] = 400
        return jmodels

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_easydiscuss:
            self._migrate_easydiscuss()

    def _migrate_easydiscuss(self):
        self.easydiscuss_tag_ids.migrate()
        self.easydiscuss_attachment_ids.migrate()
        self.easydiscuss_post_ids.migrate()
        self.easydiscuss_vote_ids.migrate()
        self.easydicuss_comment_ids.migrate()
        self.easydiscuss_post_ids.post_migrate()
