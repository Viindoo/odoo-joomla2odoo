from odoo import  models


class Blog(models.Model):
    _inherit = 'blog.blog'

    def all_tags(self, min_limit=1):
        tag_by_blog = super(Blog, self).all_tags(min_limit)
        if self.env.context.get('blog_filter_by_language', False):
            language_code = self.env.context.get('lang')
            for blog_id in tag_by_blog:
                tags = tag_by_blog[blog_id]
                filtered_tags = tags.filtered(
                    lambda tag: tag.post_ids.filtered(
                        lambda post: (not post.language_id or
                                      post.language_id.code == language_code)
                    )
                )
                tag_by_blog[blog_id] = filtered_tags
        return tag_by_blog

