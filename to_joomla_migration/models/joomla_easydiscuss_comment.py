from odoo import models, fields


class EasyDiscussComment(models.TransientModel):
    _name = 'joomla.easydiscuss.comment'
    _inherit = 'abstract.joomla.model'
    _description = 'EasyDiscuss Comment'
    _joomla_table = 'discuss_comments'

    comment = fields.Text(joomla_column=True)
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    user_id = fields.Many2one('joomla.user', joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    odoo_id = fields.Many2one('mail.message')

    def _prepare_mail_message_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        author = self.user_id.odoo_id or self._get_default_partner()
        comment = self._get_html_comment()
        values.update(
            author_id=author.id,
            model='forum.post',
            res_id=self.post_id.odoo_id.id,
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

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_mail_message_values()
        comment = self.env['mail.message'].create(values)
        return comment
