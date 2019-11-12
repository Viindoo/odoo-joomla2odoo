from odoo import models, fields


class JoomlaTag(models.TransientModel):
    _inherit = 'joomla.tag'

    website_doc_tag_id = fields.Many2one('website.doc.tag')

    def _prepare_website_doc_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(name=self.name)
        return values

    def migrate_to_website_doc_tag(self):
        tags = self.env['website.doc.tag'].search([])
        tag_names = {r.name: r for r in tags}
        for jtag in self:
            if jtag.website_doc_tag_id:
                continue
            tag = tag_names.get(jtag.name)
            if not tag:
                values = jtag._prepare_website_doc_tag_values()
                tag = tags.create(values)
            jtag.website_doc_tag_id = tag
