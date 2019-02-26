# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    def _prepare_doc_content_values(self, article):
        values = super(JoomlaMigration, self)._prepare_doc_content_values(article)
        values.update(odoo_version_id=self.env.ref('to_odoo_version.odoo_v8').id)
        return values
