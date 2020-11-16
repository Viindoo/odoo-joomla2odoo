from odoo import  models


class Blog(models.Model):
    _inherit = 'blog.blog'

    def all_tags(self, join=False, min_limit=1):
        tag_by_blog = super(Blog, self).all_tags(join, min_limit)
        if self.env.context.get('blog_filter_by_language', False):
            language_code = self.env.context.get('lang', '')
            if join:
                return tag_by_blog._filter_tags(language_code)
            for key, tags in tag_by_blog.items():
                tags = tags._filter_tags(language_code)
        return tag_by_blog

