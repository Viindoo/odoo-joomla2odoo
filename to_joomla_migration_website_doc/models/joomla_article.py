import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class JoomlaArticle(models.TransientModel):
    _inherit = 'joomla.article'

    website_doc_id = fields.Many2one('website.document')

    def _prepare_website_doc_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        author = self.author_id.odoo_user_id.partner_id or self._get_default_partner()
        tags = self.tag_ids.mapped('website_doc_tag_id')
        values.update(
            name=self.name,
            lang_ids=[(4, self.language_id.id, 0)],
            author_id=author.id,
            tag_ids=[(6, 0, tags.ids)]
        )
        return values

    def _prepare_website_doc_content_values(self):
        self.ensure_one()
        content = self._migrate_html(self.introtext + self.fulltext)
        values = dict(
            fulltext=content,
            parent_id=self.website_doc_id.id
        )
        return values

    def _migrate_to_website_doc(self, doc_category, sequence=None):
        self.ensure_one()
        doc_values = self._prepare_website_doc_values()
        doc_values.update(category_id=doc_category.id)
        if sequence:
            doc_values.update(sequence=sequence)
        self.website_doc_id = self.env['website.document'].create(doc_values)
        doc_content_values = self._prepare_website_doc_content_values()
        self.env['website.document.content'].create(doc_content_values)
        self._add_url_map(self.sef_url, self.website_doc_id.sef_url)

    def migrate_to_website_doc(self, category_map):
        jobs = []

        for xml_id, data in category_map.items():
            doc_category = self.env.ref(xml_id)

            article_ids = []
            article_category_ids = []
            for i in data:
                if isinstance(i, int):
                    article_category_ids.append(i)
                elif isinstance(i, list):
                    article_ids += i

            sequence = 10

            article_categories = self.env['joomla.category'].search([('joomla_id', 'in', article_category_ids)])
            for article_category in article_categories:
                articles = self.filtered(lambda r: article_category in r.category_ids)
                articles = articles.sorted('ordering')
                for article in articles:
                    jobs.append((article, doc_category, sequence))
                    sequence += 1

            articles = self.filtered(lambda a: a.joomla_id in article_ids)
            for article in articles:
                jobs.append((article, doc_category, sequence))
                sequence += 1

        migrated_data_map = self.env['website.document'].get_migrated_data_map()
        for idx, (article, doc_category, sequence) in enumerate(jobs, start=1):
            _logger.info('[{}/{}] migrating doc {} in category {}'.format(idx, len(jobs), article.name, doc_category.name))
            if article.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                article.website_doc_id = migrated_data_map[article.joomla_id]
            else:
                article._migrate_to_website_doc(doc_category, sequence)
