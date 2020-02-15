from odoo import models


class Post(models.Model):
    _inherit = 'forum.post'

    def _get_post_karma_rights(self):
        if self._context.get('joomla_migration'):
            for post in self:
                post.can_ask = True
                post.can_answer = True
                post.can_upvote = True
                post.can_downvote = True
                post.can_comment = True
                post.can_post = True
                post.can_edit = True
        else:
            super(Post, self)._get_post_karma_rights()

    def _update_content(self, content, forum_id):
        if self._context.get('joomla_migration'):
            return content
        return super(Post, self)._update_content(content, forum_id)
