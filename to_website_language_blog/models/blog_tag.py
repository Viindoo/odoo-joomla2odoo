from odoo import  models


class BlogTag(models.Model):
    _inherit = 'blog.tag'

    def _filter_tags(self, language_code):
        return self.filtered(
                    lambda tag: tag.post_ids.filtered(
                        lambda post: (not post.language_id or
                                      post.language_id.code == language_code)
                    )
                )

