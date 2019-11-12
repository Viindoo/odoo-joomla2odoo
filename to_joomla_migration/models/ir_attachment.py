from odoo import models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def get_image_url(self):
        self.ensure_one()
        if self.mimetype and self.mimetype.startswith('image'):
            return '/web/image/{}/{}'.format(self.id, self.name)
        return None

    def get_content_url(self, download=True):
        self.ensure_one()
        url = '/web/content/{}'.format(self.id)
        if download:
            url += '?download=true'
        return url
