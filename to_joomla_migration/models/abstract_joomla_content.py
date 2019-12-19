import logging

import lxml.html

from odoo import models, release
from odoo.tools import html_sanitize

_logger = logging.getLogger(__name__)


def _get_bootstrap_version():
    odoo_version = release.version_info[0]
    if odoo_version == 12:
        return 4
    elif odoo_version == 11:
        return 3
    return None


def _get_responsive_img_class():
    version = _get_bootstrap_version()
    if version == 4:
        return 'img-fluid'
    elif version == 3:
        return 'img-responsive'
    return ''


class AbstractJoomlaContent(models.AbstractModel):
    _name = 'abstract.joomla.content'
    _inherit = 'abstract.joomla.model'
    _description = 'Abstract Joomla Content'

    responsive_img_class = _get_responsive_img_class()

    def _migrate_image(self, image_url):
        self.ensure_one()
        if not self.migration_id._is_internal_url(image_url):
            return image_url
        attachment = self._migrate_attachment(image_url)
        if attachment:
            return attachment.get_image_url()
        return None

    def _migrate_html(self, html, to_xml=False):
        html = self._sanitize_html(html)
        html_doc = lxml.html.fromstring(html)
        self._migrate_html_doc(html_doc)
        output_type = 'xml' if to_xml else 'html'
        return lxml.html.tostring(html_doc, encoding='unicode', method=output_type)

    def _sanitize_html(self, html):
        html = html.replace('lang:php=""', '') \
            .replace('lang:php=', '') \
            .replace('lang:php', '') \
            .replace('xml:lang="css"', '') \
            .replace('xml:lang="php"', '') \
            .replace('xml:lang="xml"', '') \
            .replace('xml:lang="python"', '')
        html = html_sanitize(html)
        return html

    def _migrate_html_doc(self, html_doc):
        self._migrate_image_in_html(html_doc)

    def _migrate_image_in_html(self, html_doc):
        imgs = html_doc.findall('.//img')
        for img in imgs:
            url = img.get('src')
            if url:
                new_url = self._migrate_image(url)
                if new_url:
                    img.set('src', new_url)
                    if self.responsive_img_class:
                        img.classes.add(self.responsive_img_class)

    def _prepare_blog_post_content(self, content, intro_image_url=None):
        content = self._migrate_html(content)
        if intro_image_url:
            intro_image_url = self._migrate_image(intro_image_url)
        if intro_image_url:
            content = """
                <p>
                    <img src="{}" class="center-block {}"/>
                </p>
            """.format(intro_image_url, self.responsive_img_class) + content
        content = """
            <section class="s_text_block">
                <div class="container">
                    {}
                </div>
            </section>
        """.format(content)
        return content

    def _add_url_map(self, from_url, to_url, redirect=True):
        return self.migration_id._add_url_map(from_url, to_url, redirect)
