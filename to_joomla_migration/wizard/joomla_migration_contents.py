import logging
import re
import urllib.parse

import lxml.html

from odoo import models, fields

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    website_page_ids = fields.One2many('website.page', 'migration_id')
    blog_post_ids = fields.One2many('blog.post', 'migration_id')

    def _post_migrate_data(self):
        super(JoomlaMigration, self)._post_migrate_data()
        self._update_href()

    def _update_href(self):
        for idx, page in enumerate(self.website_page_ids, start=1):
            _logger.info('[{}/{}] updating href in page {}'.format(idx, len(self.website_page_ids), page.name))
            content = self._update_href_in_content(page.view_id.arch_base, 'xml')
            page.view_id.arch_base = content

        for idx, post in enumerate(self.blog_post_ids, start=1):
            _logger.info('[{}/{}] updating href in blog post {}'.format(idx, len(self.blog_post_ids), post.name))
            content = self._update_href_in_content(post.content)
            post.content = content

    def _update_href_in_content(self, content, output_type='html'):
        et = lxml.html.fromstring(content)
        a_tags = et.findall('.//a')
        for a in a_tags:
            url = a.get('href')
            if url and (url.startswith('mailto:') or url.startswith('#')):
                continue
            if url and self._is_internal_url(url):
                url = re.sub(r'^https?://[^/]+', '', url)  # convert to relative url
                if '%' in url:
                    url = urllib.parse.unquote(url)
                if not url.startswith('/'):
                    url = '/' + url
                url_map = self._get_url_map(url)
                if not url_map:
                    a.drop_tag()
                    _logger.info('dropped href {}'.format(url))
                else:
                    new_url = url_map.to_url
                    a.set('href', new_url)
                    _logger.info('converted href from {} to {}'.format(url, new_url))
        return lxml.html.tostring(et, encoding='unicode', method=output_type)

    def _is_internal_url(self, url):
        url_com = urllib.parse.urlparse(url)
        if not url_com.netloc:
            return True
        website_url_com = urllib.parse.urlparse(self.website_url)
        return url_com.netloc == website_url_com.netloc
