# -*- coding: utf-8 -*-
import logging
import re

import lxml.html

from odoo import fields, models, release

_logger = logging.getLogger(__name__)

_bootstrap_replacement_rules = {
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
    ]
}


def _migrate_bootstrap(html, from_version, to_version):
    from_version, to_version = int(from_version), int(to_version)

    rules = []
    for v in range(from_version, to_version):
        rules.extend(_bootstrap_replacement_rules[v])

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

    return lxml.html.tostring(element, encoding='unicode')


class BootstrapMigration(models.TransientModel):
    _name = 'bootstrap.migration'
    _description = 'Bootstrap Migration'

    def _bootstrap_version(self):
        odoo_version = release.version_info[0]
        if odoo_version == 12:
            return 4
        elif odoo_version == 11:
            return 3
        return False

    def _supported_versions(self):
        versions = [(2, '2'), (3, '3')]
        to_version = self._bootstrap_version()
        supported_versions = [v for v in versions if v[0] < to_version]
        return supported_versions

    from_version = fields.Selection(selection=_supported_versions, required=True)
    to_version = fields.Integer(default=_bootstrap_version, readonly=True)

    def run(self):
        self.ensure_one()
        self._migrate_bootstrap_in_blog_posts()

    def _migrate_bootstrap_in_blog_posts(self):
        posts = self.env['blog.post'].search([])
        for post in posts:
            _logger.info('migrating bootstrap in blog post {}'.format(post.name))
            new_content = _migrate_bootstrap(post.content, self.from_version,
                                             self.to_version)
            post.content = new_content
