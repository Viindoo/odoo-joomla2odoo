import urllib.parse

from odoo import models, fields
from odoo.http import request


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    url_map_ids = fields.One2many('joomla.migration.url.map', 'migration_id')
    redirect = fields.Boolean(default=False)

    def _post_migrate_data(self):
        super(JoomlaMigration, self)._post_migrate_data()
        if self.redirect:
            self._create_redirects()

    def _create_redirects(self):
        Website = self.env['website']
        from_domain = urllib.parse.urlparse(self.website_url).hostname
        from_website = Website.search([('domain', '=', from_domain)], limit=1)
        if not from_website:
            values = {
                'name': from_domain,
                'domain': from_domain
            }
            from_website = Website.create(values)

        Redirect = self.env['website.redirect']
        from_urls = set(Redirect.search([]).mapped('url_from'))
        for item in self.url_map_ids:
            if not item.redirect or item.from_url in from_urls:
                continue
            values = {
                'type': '301',
                'url_from': item.from_url,
                'url_to': item.to_url,
                'website_id': from_website.id,
                'migration_id': self.id,
                'old_website': self.website_url
            }
            Redirect.create(values)

    def _get_website_url(self):
        request_url = request.httprequest.url_root
        request_url_components = urllib.parse.urlparse(request_url)
        url = '{}://{}'.format(request_url_components.scheme, self.to_website_id.domain)
        if request_url_components.port:
            url += ':{}'.format(request_url_components.port)
        return url

    def _add_url_map(self, from_url, to_url, redirect=True):
        if not from_url or not to_url:
            return None
        to_url = urllib.parse.urljoin(self._get_website_url(), to_url)
        values = dict(
            migration_id=self.id,
            from_url=from_url,
            to_url=to_url,
            redirect=redirect
        )
        return self.env['joomla.migration.url.map'].create(values)

    def _get_url_map(self, from_url):
        return self.env['joomla.migration.url.map'].search([('from_url', '=', from_url)], limit=1)

    def _get_records_to_reset(self):
        res = super(JoomlaMigration, self)._get_records_to_reset()
        redirects = self.env['website.redirect'].get_migrated_data()
        res.extend([(redirects, 1100)])
        return res


class JoomlaMigrationUrlMap(models.TransientModel):
    _name = 'joomla.migration.url.map'
    _description = 'Joomla Migration URL Map'

    migration_id = fields.Many2one('joomla.migration', required=True, ondelete='cascade')
    from_url = fields.Char(required=True)
    to_url = fields.Char(required=True)
    redirect = fields.Boolean(default=True)
