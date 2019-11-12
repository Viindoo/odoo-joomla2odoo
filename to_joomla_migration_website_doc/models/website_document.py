from odoo import models, fields


class WebsiteDocument(models.Model):
    _name = 'website.document'
    _inherit = ['website.document', 'abstract.joomla.migration.track']

    sef_url = fields.Char(compute='_compute_sef_url')

    def _compute_sef_url(self):
        for doc in self:
            url = doc.get_website_url()
            if doc.lang_ids:
                url = '/' + doc.lang_ids[0].code + url
            doc.sef_url = url
