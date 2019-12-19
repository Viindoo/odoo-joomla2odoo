from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify


class ForumPost(models.Model):
    _inherit = 'forum.post'

    sef_url = fields.Char(compute='_compute_sef_url')

    @api.depends('name', 'forum_id.name')
    def _compute_sef_url(self):
        for post in self:
            if post.name:
                url = '/forum/{}-{}/question/{}-{}'.format(
                    slugify(post.forum_id.name), post.forum_id.id,
                    slugify(post.name), post.id)
                post.sef_url = url
            else:
                post.sef_url = False

    def post_notification(self):
        if not self._context.get('joomla_migration'):
            return super(ForumPost, self).post_notification()