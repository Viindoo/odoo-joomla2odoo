from odoo import models, fields


class JoomlaTag(models.TransientModel):
    _inherit = 'joomla.tag'

    odoo_doc_tag_id = fields.Many2one('website.doc.tag')

    def _prepare_website_doc_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(name=self.name)
        return values

    def _migrate_to_website_doc_tag(self, matching_record):
        self.ensure_one()
        if matching_record:
            return matching_record
        values = self._prepare_website_doc_tag_values()
        tag = self.env['website.doc.tag'].create(values)
        return tag

    def migrate_to_website_doc_tag(self):
        super(JoomlaTag, self).migrate(result_field='odoo_doc_tag_id', meth='_migrate_to_website_doc_tag')
