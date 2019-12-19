from odoo import models, fields, api


class EasyDiscussAttachment(models.TransientModel):
    _name = 'joomla.easydiscuss.attachment'
    _inherit = 'abstract.joomla.model'
    _description = 'EasyDiscuss Attachment'
    _joomla_table = 'discuss_attachments'

    name = fields.Char(joomla_column='title')
    post_id = fields.Many2one('joomla.easydiscuss.post', joomla_column='uid')
    mime = fields.Char(joomla_column=True)
    download_url = fields.Char(compute='_compute_download_url')
    odoo_id = fields.Many2one('ir.attachment')

    @api.depends('post_id.language_id')
    def _compute_download_url(self):
        for r in self:
            if r.post_id.language_id:
                r.download_url = '/{}/discussions?controller=attachment&task=download&tmpl=component&id={}'.format(
                    r.post_id.language_id.code[:2], r.joomla_id)
            else:
                r.download_url = False

    def _migrate(self):
        self.ensure_one()
        attachment = self._migrate_attachment(self.download_url, self.name)
        return attachment
