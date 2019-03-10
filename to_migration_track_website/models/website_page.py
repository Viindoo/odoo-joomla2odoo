from odoo import api, fields, models


class WebsitePage(models.Model):
    _name = 'website.page'
    _inherit = ['website.page', 'abstract.joomla.migration.track']

    sef_url = fields.Char(compute='_compute_sef_url', store=True)

    @api.depends('url', 'language_id', 'language_id.code')
    def _compute_sef_url(self):
        for page in self:
            if page.language_id:
                page.sef_url = '/' + page.language_id.code + page.url
            else:
                page.sef_url = page.url

