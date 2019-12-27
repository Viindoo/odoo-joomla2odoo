from odoo import models, fields, SUPERUSER_ID


class EasyDiscussVote(models.TransientModel):
    _name = 'joomla.easydiscuss.vote'
    _description = 'EasyDiscuss Vote'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'discuss_votes'

    user_id = fields.Many2one('joomla.user', joomla_column=True)
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    value = fields.Integer(joomla_column=True)
    odoo_id = fields.Many2one('forum.post.vote')

    def _prepare_forum_post_vote_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            post_id=self.post_id.odoo_id.id,
            user_id=self.user_id.odoo_id.user_ids[:1].id or SUPERUSER_ID,
            vote=str(self.value),
            forum_id=self.migration_id.to_forum_id.id
        )
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_forum_post_vote_values()
        post = self.env['forum.post'].browse(values.get('post_id'))
        if not post:
            self._logger.warning('ignore, no post for vote')
        elif post.create_uid.id == values.get('user_id'):
            self._logger.warning('ignore, it is not allowed to vote for its own post')
        else:
            vote = self.env['forum.post.vote'].create(values)
            return vote
        return self.env['forum.post.vote']
