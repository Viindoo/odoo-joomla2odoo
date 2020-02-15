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
        self.ensure_one()
        Redirect = self.env['website.redirect']
        from_urls = set(Redirect.search([]).mapped('url_from'))
        for item in self.url_map_ids:
            if not item.redirect or item.from_url in from_urls:
                continue
            values = {
                'type': '301',
                'url_from': item.from_url,
                'url_to': item.to_url,
                'website_id': self.to_website_id.id,
                'migration_id': self.id,
                'old_website': self.website_url
            }
            Redirect.create(values)

    def _get_to_website_url(self):
        domain = self.to_website_id.domain
        if not domain:
            return None
        components = urllib.parse.urlparse(domain)
        if components.scheme:
            return domain
        components = urllib.parse.urlparse(request.httprequest.url_root)
        url = '{}://{}'.format(components.scheme, domain)
        if components.port:
            url += ':{}'.format(components.port)
        return url

    def _process_to_url_for_map(self, to_url):
        to_website_url = self._get_to_website_url()
        if to_website_url and to_website_url != self.website_url:
            to_url = urllib.parse.urljoin(to_website_url, to_url)
        return to_url

    def _add_url_map(self, from_url, to_url, redirect=True):
        self.ensure_one()
        if not from_url or not to_url:
            return None
        to_url = self._process_to_url_for_map(to_url)
        values = dict(
            migration_id=self.id,
            from_url=from_url,
            to_url=to_url,
            redirect=redirect
        )
        return self.env['joomla.migration.url.map'].create(values)

    def _get_to_url(self, from_url):
        return self.env['joomla.migration.url.map'].search([('from_url', '=', from_url)], limit=1).to_url


class JoomlaMigrationUrlMap(models.TransientModel):
    _name = 'joomla.migration.url.map'
    _description = 'Joomla Migration URL Map'

    migration_id = fields.Many2one('joomla.migration', required=True, ondelete='cascade')
    from_url = fields.Char(required=True)
    to_url = fields.Char(required=True)
    redirect = fields.Boolean(default=True)
