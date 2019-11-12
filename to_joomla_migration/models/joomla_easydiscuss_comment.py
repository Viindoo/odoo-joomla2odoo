import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class EasyDiscussComment(models.TransientModel):
    _name = 'joomla.easydiscuss.comment'
    _inherit = 'abstract.joomla.model'
    _description = 'EasyDiscuss Comment'
    _joomla_table = 'discuss_comments'

    comment = fields.Text(joomla_column=True)
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    user_id = fields.Many2one('joomla.user', joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    forum_post_comment_id = fields.Many2one('mail.message')

    def _prepare_forum_post_comment_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        author = self.user_id.odoo_user_id.partner_id or self._get_default_partner()
        comment = self._get_html_comment()
        values.update(
            author_id=author.id,
            model='forum.post',
            res_id=self.post_id.forum_post_id.id,
            body=comment,
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_comment').id,
            date=self.created
        )
        return values

    def _get_html_comment(self):
        self.ensure_one()
        comment = self.comment.replace('\n', '<br>')
        return comment

    def _migrate_to_forum_post_comment(self):
        self.ensure_one()
        values = self._prepare_forum_post_comment_values()
        self.forum_post_comment_id = self.env['mail.message'].create(values)

    def migrate_to_forum_post_comment(self):
        migrated_data_map = self.env['mail.message'].get_migrated_data_map()
        for idx, comment in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating easydiscuss comment'.format(idx, len(self)))
            if comment.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                comment.forum_post_comment_id = migrated_data_map[comment.joomla_id]
            else:
                comment._migrate_to_forum_post_comment()
                self._cr.commit()
