from odoo import models, fields


class EasyBlogTag(models.TransientModel):
    _name = 'joomla.easyblog.tag'
    _description = 'EasyBlog Tag'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'easyblog_tag'

    name = fields.Char(joomla_column='title')
    odoo_id = fields.Many2one('blog.tag')

    def _prepare_blog_tag_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(name=self.name)
        return values

    def _get_matching_data(self, odoo_model):
        return self._get_matching_data_by_name(odoo_model)

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_blog_tag_values()
        tag = self.env['blog.tag'].create(values)
        return tag
