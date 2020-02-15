import re
import urllib.parse

import lxml.html

from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    website_page_ids = fields.One2many('website.page', 'migration_id')
    blog_post_ids = fields.One2many('blog.post', 'migration_id')

    def _post_migrate_data(self):
        super(JoomlaMigration, self)._post_migrate_data()
        self._update_href()

    def _update_href(self):
        for idx, page in enumerate(self.website_page_ids, start=1):
            self._logger.info('[{}/{}] updating href in page {}'.format(idx, len(self.website_page_ids), page.name))
            content = self._update_href_in_content(page.view_id.arch_base, 'xml')
            page.view_id.arch_base = content

        for idx, post in enumerate(self.blog_post_ids, start=1):
            self._logger.info('[{}/{}] updating href in blog post {}'.format(idx, len(self.blog_post_ids), post.name))
            content = self._update_href_in_content(post.content)
            post.content = content

    def _update_href_in_content(self, content, output_type='html'):
        et = lxml.html.fromstring(content)
        tags = et.findall('.//a')
        for tag in tags:
            url = tag.get('href')
            if url and (url.startswith('mailto:') or url.startswith('#')):
                continue
            if url and self._is_internal_url(url):
                url = self._make_sef_url(url)
                url = re.sub(r'^https?://[^/]+', '', url)  # convert to relative url
                if '%' in url:
                    url = urllib.parse.unquote(url)
                if not url.startswith('/'):
                    url = '/' + url
                new_url = self._get_to_url(url)
                if new_url:
                    tag.set('href', new_url)
                    self._logger.info('converted href from {} to {}'.format(url, new_url))
                else:
                    del tag.attrib['href']
                    self._logger.info('drop href {}'.format(url))
        return lxml.html.tostring(et, encoding='unicode', method=output_type)

    def _make_sef_url(self, url):
        com = urllib.parse.urlparse(url)
        if com.path == 'index.php':
            query_values = urllib.parse.parse_qs(com.query)
            if query_values.get('option') == ['com_content'] and query_values.get('view') == ['article']:
                id = query_values.get('id')
                if id:
                    id = id[0].split(':')
                    if id and id[0].isdigit():
                        id = int(id[0])
                        article = self.article_ids.filtered(lambda a: a.joomla_id == id)[:1]
                        if article:
                            return article.sef_url
        return url

    def _is_internal_url(self, url):
        url_com = urllib.parse.urlparse(url)
        if not url_com.netloc:
            return True
        website_url_com = urllib.parse.urlparse(self.website_url)
        return url_com.netloc == website_url_com.netloc
