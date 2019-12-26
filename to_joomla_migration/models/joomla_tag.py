from odoo import fields, models


class JoomlaTag(models.TransientModel):
    _name = 'joomla.tag'
    _description = 'Joomla Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'tags'

    name = fields.Char(joomla_column='title')
    odoo_blog_tag_id = fields.Many2one('blog.tag')

    def _prepare_blog_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(name=self.name)
        return values

    def _get_matching_data(self, odoo_model):
        return self._get_matching_data_by_name(odoo_model)

    def _migrate_to_blog_tag(self):
        values = self._prepare_blog_tag_values()
        tag = self.env['blog.tag'].create(values)
        return tag

    def migrate_to_blog_tag(self):
        super(JoomlaTag, self).migrate(result_field='odoo_blog_tag_id', meth='_migrate_to_blog_tag')
