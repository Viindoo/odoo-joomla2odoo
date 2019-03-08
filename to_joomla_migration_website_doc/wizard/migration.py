# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class WebsiteDocument(models.Model):
    _name = 'website.document'
    _inherit = ['website.document', 'joomla.migration.track']

    sef_url = fields.Char(compute='_compute_sef_url')

    def _compute_sef_url(self):
        for doc in self:
            url = doc.get_website_url()
            if doc.lang_ids:
                url = '/' + doc.lang_ids[0].code + url
            doc.sef_url = url


class WebsiteDocTag(models.Model):
    _name = 'website.doc.tag'
    _inherit = ['website.doc.tag', 'joomla.migration.track']


class JoomlaTag(models.TransientModel):
    _inherit = 'joomla.tag'

    odoo_website_doc_tag_id = fields.Many2one('website.doc.tag')


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    to_docs = fields.Boolean()

    def _get_category_map(self):
        """
        Return a dict that maps doc category xml id with joomla data.

        Joomla data is a list of items:
        Item is int => category id.
        Item is list => list of article ids.
        """
        return {
            'to_website_docs_odoo_data.categ_accounting': [18, 50, 88],
            'to_website_docs_odoo_data.categ_crm': [17, 87],
            'to_website_docs_odoo_data.categ_document_management': [94],
            'to_website_docs_odoo_data.categ_discuss': [[277]],
            'to_website_docs_odoo_data.categ_erponline': [83],
            'to_website_docs_odoo_data.categ_getting_started': [16, 86],
            'to_website_docs_odoo_data.categ_hr': [28, 89],
            'to_website_docs_odoo_data.categ_inventory': [58, 92],
            'to_website_docs_odoo_data.categ_marketing': [21],
            'to_website_docs_odoo_data.categ_mrp': [36, 91],
            'to_website_docs_odoo_data.categ_network_organization': [[278]],
            'to_website_docs_odoo_data.categ_odoo_admin': [44, 84],
            'to_website_docs_odoo_data.categ_process_management': [93],
            'to_website_docs_odoo_data.categ_project': [37, 90],
            'to_website_docs_odoo_data.categ_purchase': [45, 71],
            'to_website_docs_odoo_data.categ_sales': [43, 65],
            'to_website_docs_odoo_data.categ_use_cases': [79]
        }

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_article and self.to_docs:
            self._migrate_docs()

    def _migrate_docs(self):
        jobs = []

        for xml_id, data in self._get_category_map().items():
            doc_category = self.env.ref(xml_id)

            article_ids = []
            article_category_ids = []
            for i in data:
                if isinstance(i, int):
                    article_category_ids.append(i)
                elif isinstance(i, list):
                    article_ids += i

            sequence = 10

            article_categories = self.env['joomla.category'].search(
                [('joomla_id', 'in', article_category_ids)])
            for article_category in article_categories:
                articles = self.article_ids.filtered(
                    lambda r: article_category in r.category_ids)
                articles = articles.sorted('ordering')
                for article in articles:
                    jobs.append((article, doc_category, sequence))
                    sequence += 1

            articles = self.env['joomla.article'].search(
                [('joomla_id', 'in', article_ids)])
            for article in articles:
                jobs.append((article, doc_category, sequence))
                sequence += 1

        for idx, (article, doc_category, sequence) in enumerate(jobs, start=1):
            _logger.info('[{}/{}] migrating doc {} in category {}'
                         .format(idx, len(jobs), article.name, doc_category.name))
            self._migrate_article_to_doc(article, doc_category, sequence)

    def _migrate_article_to_doc(self, article, doc_category, sequence=None):
        author = article.author_id.odoo_user_id.partner_id
        if not author:
            author = self.env.user.partner_id
        self._migrate_article_tag_to_doc_tag(article)
        tags = article.tag_ids.mapped('odoo_website_doc_tag_id')
        doc_values = {
            'name': article.name,
            'category_id': doc_category.id,
            'lang_ids': [(4, article.odoo_compat_lang_id.id, 0)],
            'author_id': author.id,
            'tag_ids': [(6, 0, tags.ids)],
            'migration_id': self.id,
        }
        if sequence:
            doc_values.update(sequence=sequence)
        doc = self.env['website.document'].create(doc_values)
        doc_content_values = self._prepare_doc_content_values(article)
        doc_content_values.update(parent_id=doc.id)
        self.env['website.document.content'].create(doc_content_values)
        self._add_url_map(article.sef_url, doc.sef_url)
        return doc

    def _prepare_doc_content_values(self, article):
        content = article.introtext + article.fulltext
        content = self._convert_content_common(content)
        return {
            'fulltext': content
        }

    def _migrate_article_tag_to_doc_tag(self, article):
        doc_tags = self.env['website.doc.tag'].search([])
        doc_tag_names = {r.name: r for r in doc_tags}
        for tag in article.tag_ids:
            if tag.odoo_website_doc_tag_id:
                continue
            doc_tag = doc_tag_names.get(tag.name)
            if not doc_tag:
                values = {
                    'name': tag.name,
                    'migration_id': self.id
                }
                doc_tag = self.env['website.doc.tag'].create(values)
            tag.odoo_website_doc_tag_id = doc_tag.id

    def _update_href(self):
        super(JoomlaMigration, self)._update_href()
        contents = self.env['website.document'].search(
            [('migration_id', '=', self.id)]).mapped('content_ids')
        for idx, content in enumerate(contents, start=1):
            _logger.info('[{}/{}] updating href in doc {}'
                         .format(idx, len(contents), content.parent_id.name))
            fulltext = self._update_href_for_content(content.fulltext)
            content.fulltext = fulltext

    def reset(self):
        self.ensure_one()
        super(JoomlaMigration, self).reset()

        _logger.info('removing website docs')
        created_by_migration = ('migration_id', '!=', False)
        self.env['website.document'].search([created_by_migration]).unlink()
        self.env['website.doc.tag'].search([created_by_migration]).unlink()
