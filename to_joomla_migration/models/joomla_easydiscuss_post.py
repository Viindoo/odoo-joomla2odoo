import logging

import bbcode

from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class EasyDiscussPost(models.TransientModel):
    _name = 'joomla.easydiscuss.post'
    _description = 'EasyDiscuss Post'
    _inherit = 'abstract.joomla.content'
    _joomla_table = 'discuss_posts'

    name = fields.Char(joomla_column='title')
    alias = fields.Char(joomla_column=True)
    category_id = fields.Many2one('joomla.easydiscuss.category', joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    modified_date = fields.Datetime(joomla_column='modified')
    content = fields.Text(joomla_column=True)
    content_type = fields.Char(joomla_column=True)
    language = fields.Char(joomla_column=True, string='Language Code')
    hits = fields.Integer(joomla_column=True)
    answered = fields.Integer(joomla_column=True)
    user_id = fields.Many2one('joomla.user', joomla_column=True)
    parent_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    tag_ids = fields.Many2many('joomla.easydiscuss.tag', compute='_compute_tags')
    attachment_ids = fields.One2many('joomla.easydiscuss.attachment', 'post_id')
    sef_url = fields.Char(compute='_compute_sef_url')
    forum_post_id = fields.Many2one('forum.post')
    language_id = fields.Many2one('res.lang', compute='_compute_language')

    def _compute_tags(self):
        post_tag = self.env['joomla.easydiscuss.post.tag'].search([('post_id', 'in', self.ids)])
        for post in self:
            post.tag_ids = post_tag.filtered(lambda pt: pt.post_id == post).mapped('tag_id')

    def _compute_language(self):
        for post in self:
            lang = self._get_lang_from_code(post.language)
            if not lang:
                lang = self._get_lang_from_code(post.category_id.language)
            post.language_id = lang

    @api.depends('alias', 'language_id')
    def _compute_sef_url(self):
        for post in self:
            if post.language_id:
                post.sef_url = '{}/discussions/{}-{}'.format(post.language_id.code[:2], post.joomla_id, post.alias)
            else:
                post.sef_url = False

    def _prepare_forum_post_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        content = self._prepare_forum_post_content()
        tags = self.tag_ids.mapped('forum_tag_id')
        values.update(
            name=self.name if not self.parent_id else False,
            content=content,
            parent_id=self.parent_id.forum_post_id.id,
            website_id=self.migration_id.to_website_id.id,
            forum_id=self.migration_id.to_forum_id.id,
            tag_ids=[(6, 0, tags.ids)],
            is_correct=self.answered,
            views=self.hits
        )
        return values

    def _prepare_forum_post_content(self):
        self.ensure_one()
        if self.content_type == 'bbcode':
            parser = self._get_bbcode_parser()
            html = parser.format(self.content)
        else:
            html = self.content
        html = self._migrate_html(html)
        attachments = self.attachment_ids.mapped('attachment_id')
        for at in attachments:
            url = at.get_image_url()
            if url:
                html += """
                    <p>
                        <img class="{}" src="{}" title="{}"
                    </p>
                """.format(self.responsive_img_class, url, at.name)
                continue
            url = at.get_content_url()
            if url:
                html += """
                    <p>
                        <a href="{}" class="o_image" title="{}"
                    </p>
                """.format(url, at.name)
        return html

    def _get_bbcode_parser(self):
        parser = bbcode.Parser(replace_links=False)
        parser.add_simple_formatter('img', '<img src="%(value)s">')
        # TODO: add formatters for some video sites such as youtube,...
        parser.add_simple_formatter('video', ' %(value)s ')
        return parser

    def _migrate_to_forum_post(self):
        self.ensure_one()
        values = self._prepare_forum_post_values()
        post = self.env['forum.post'].create(values)
        user_id = self.user_id.odoo_user_id.id or SUPERUSER_ID
        sql = """
            UPDATE forum_post
            SET create_uid = %s,
                create_date = %s,
                write_uid = %s
            WHERE id = %s
            """
        self._cr.execute(sql, (user_id, self.created, user_id, post.id))
        post.create_uid = user_id  # update cache
        self.forum_post_id = post
        self._add_url_map(self.sef_url, post.sef_url)

    def migrate_to_forum_post(self):
        migrated_data_map = self.env['forum.post'].get_migrated_data_map()
        for idx, post in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating easydiscuss post {}'.format(idx, len(self), post.alias))
            if post.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                post.forum_post_id = migrated_data_map[post.joomla_id]
            else:
                post._migrate_to_forum_post()
                self._cr.commit()

    def update_write_date(self):
        for idx, post in enumerate(self, start=1):
            _logger.info('[{}/{}] updating write date for forum post {}'.format(idx, len(self), post.alias))
            if post.forum_post_id:
                sql = "UPDATE forum_post SET write_date = %s WHERE id = %s"
                self._cr.execute(sql, (post.modified_date, post.forum_post_id.id))
                self._cr.commit()
