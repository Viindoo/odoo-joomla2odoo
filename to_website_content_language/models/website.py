from odoo import fields, models


class WebsitePage(models.Model):
    _inherit = 'website.page'

    def _get_current_language(self):
        language_code = self.env.context.get('lang')
        language = self.env['res.lang'].search([('code', '=', language_code)], limit=1)
        return language.id

    language_id = fields.Many2one('res.lang', default=_get_current_language)
