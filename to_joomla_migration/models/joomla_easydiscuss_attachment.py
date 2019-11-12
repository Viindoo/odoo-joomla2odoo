import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EasyDiscussAttachment(models.TransientModel):
    _name = 'joomla.easydiscuss.attachment'
    _inherit = 'abstract.joomla.model'
    _description = 'EasyDiscuss Attachment'
    _joomla_table = 'discuss_attachments'

    name = fields.Char(joomla_column='title')
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column='uid')
    mime = fields.Char(joomla_column=True)
    download_url = fields.Char(compute='_compute_download_url')
    attachment_id = fields.Many2one('ir.attachment')

    @api.depends('post_id.language_id')
    def _compute_download_url(self):
        for r in self:
            if r.post_id.language_id:
                r.download_url = '/{}/discussions?controller=attachment&task=download&tmpl=component&id={}'.format(
                    r.post_id.language_id.code[:2], r.joomla_id)
            else:
                r.download_url = False

    def migrate_to_ir_attachment(self):
        migrated_data_map = self.env['ir.attachment'].get_migrated_data_map(jtable=self._get_jtable_fullname())
        for idx, jattachment in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating easydiscuss attachment {}'.format(idx, len(self), jattachment.name))
            if jattachment.download_url:
                attachment = migrated_data_map.get(jattachment.joomla_id)
                if not attachment:
                    attachment = jattachment._migrate_attachment(jattachment.download_url, jattachment.name)
                    if attachment:
                        self._cr.commit()
                else:
                    _logger.info('ignore, already migrated')
                jattachment.attachment_id = attachment
