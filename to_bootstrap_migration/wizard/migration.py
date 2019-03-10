import logging
import re

import lxml.html

from odoo import api, fields, models, release

_logger = logging.getLogger(__name__)


class BootstrapMigration(models.TransientModel):
    _name = 'bootstrap.migration'
    _description = 'Bootstrap Migration'

    def _current_version(self):
        odoo_version = release.version_info[0]
        if odoo_version == 12:
            return 4
        elif odoo_version == 11:
            return 3
        return False

    def _supported_versions(self):
        versions = [('2', '2'), ('2', '3')]
        to_version = self._current_version()
        supported_versions = [v for v in versions if int(v[0]) < to_version]
        return supported_versions

    from_version = fields.Selection(selection=_supported_versions, required=True)
    to_version = fields.Integer(default=_current_version, readonly=True)

    def run(self):
        self.ensure_one()
        self._migrate_blog_posts()

    @api.model
    def _migrate_blog_posts(self):
        posts = self.env['blog.post'].search([])
        for post in posts:
            _logger.info('migrating bootstrap in blog post {}'.format(post.name))
            new_content = self._migrate_content(post.content, self.from_version,
                                                self.to_version)
            post.content = new_content

    @api.model
    def _migration_rules(self):
        return {
            # 2 -> 3
            2: [
                (r'(?<!\S)row-fluid(?!\S)', 'row'),
                (r'(?<!\S)span(?=([0-9]|10|11|12)(\s|$))', 'col-md-')
            ],
            # 3 -> 4
            3: [
                (r'(?<!\S)col-xs-(?=([0-9]|10|11|12)(\s|$))', 'col-'),
                (r'(?<!\S)col-sm-(?=([0-9]|10|11|12)(\s|$))', 'col-md'),
                (r'(?<!\S)col-md-(?=([0-9]|10|11|12)(\s|$))', 'col-lg'),
                (r'(?<!\S)col-lg-(?=([0-9]|10|11|12)(\s|$))', 'col-xl'),
                (r'(?<!\S)img-responsive(\s|$))', 'img-fluid')
            ]
        }

    @api.model
    def _migrate_content(self, html, from_version, to_version, output='html'):
        from_version, to_version = int(from_version), int(to_version)

        all_rules = self._migration_rules()
        rules = []
        for v in range(from_version, to_version):
            rules.extend(all_rules[v])

        element = lxml.html.fromstring(html)
        class_attr_elements = element.findall('.//*[@class]')
        for el in class_attr_elements:
            before = list(el.classes)

            new_classes = []
            for c in el.classes:
                for rule in rules:
                    c = re.sub(*rule, c)
                if c:
                    new_classes.append(c)
            el.set('class', ' '.join(new_classes))

            after = list(el.classes)
            if after != before:
                _logger.info('{} -> {}'.format(before, after))

        return lxml.html.tostring(element, encoding='unicode', method=output)
