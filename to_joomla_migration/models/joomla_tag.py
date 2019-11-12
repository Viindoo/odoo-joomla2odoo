from odoo import fields, models


class JoomlaTag(models.TransientModel):
    _name = 'joomla.tag'
    _description = 'Joomla Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'tags'

    name = fields.Char(joomla_column='title')
    blog_tag_id = fields.Many2one('blog.tag')

    def _prepare_blog_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(name=self.name)
        return values

    def migrate_to_blog_tag(self):
        tags = self.env['blog.tag'].search([])
        tag_names = {r.name: r for r in tags}
        for jtag in self:
            tag = tag_names.get(jtag.name)
            if not tag:
                values = jtag._prepare_blog_tag_values()
                tag = tags.create(values)
            jtag.blog_tag_id = tag
