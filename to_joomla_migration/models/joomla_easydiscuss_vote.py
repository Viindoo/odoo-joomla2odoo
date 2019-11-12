import logging

from odoo import models, fields, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class EasyDiscussVote(models.TransientModel):
    _name = 'joomla.easydiscuss.vote'
    _description = 'EasyDiscuss Vote'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'discuss_votes'

    user_id = fields.Many2one('joomla.user', joomla_column=True)
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    value = fields.Integer(joomla_column=True)
    forum_post_vote_id = fields.Many2one('forum.post.vote')

    def _prepare_forum_post_vote_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            post_id=self.post_id.forum_post_id.id,
            user_id=self.user_id.odoo_user_id.id or SUPERUSER_ID,
            vote=str(self.value),
            forum_id=self.migration_id.to_forum_id.id
        )
        return values

    def _migrate_to_forum_post_vote(self):
        self.ensure_one()
        values = self._prepare_forum_post_vote_values()
        post = self.env['forum.post'].browse(values.get('post_id'))
        if not post:
            _logger.warning('ignore, no post for vote')
        elif post.create_uid.id == values.get('user_id'):
            _logger.warning('ignore, it is not allowed to vote for its own post')
        else:
            self.forum_post_vote_id = self.env['forum.post.vote'].create(values)

    def migrate_to_forum_post_vote(self):
        migrated_data_map = self.env['forum.post.vote'].get_migrated_data_map()
        for idx, vote in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating easydiscuss vote'.format(idx, len(self)))
            if vote.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                vote.forum_post_vote_id = migrated_data_map[vote.joomla_id]
            else:
                vote._migrate_to_forum_post_vote()
                self._cr.commit()
