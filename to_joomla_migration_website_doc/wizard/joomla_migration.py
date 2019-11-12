# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    to_docs = fields.Boolean()
    website_document_ids = fields.One2many('website.document', 'migration_id')

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

    def _migrate_articles(self):
        if self.to_docs:
            self.article_ids.mapped('tag_ids').migrate_to_website_doc_tag()
            self.article_ids.migrate_to_website_doc(self._get_category_map())
        else:
            super(JoomlaMigration, self)._migrate_articles()

    def _update_href(self):
        super(JoomlaMigration, self)._update_href()
        contents = self.website_document_ids.mapped('content_ids')
        for idx, content in enumerate(contents, start=1):
            _logger.info('[{}/{}] updating href in doc {}'.format(idx, len(contents), content.parent_id.name))
            fulltext = self._update_href_in_content(content.fulltext)
            content.fulltext = fulltext

    def _get_records_to_reset(self):
        res = super(JoomlaMigration, self)._get_records_to_reset()
        docs = self.env['website.document'].get_migrated_data()
        tags = self.env['website.doc.tag'].get_migrated_data()
        res.extend([(docs, 500), (tags, 525)])
        return res
