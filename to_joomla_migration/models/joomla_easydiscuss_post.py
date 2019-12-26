import bbcode

from odoo import models, fields, api


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
    language_id = fields.Many2one('res.lang', compute='_compute_language')
    hits = fields.Integer(joomla_column=True)
    answered = fields.Integer(joomla_column=True)
    user_id = fields.Many2one('joomla.user', joomla_column=True)
    parent_id = fields.Many2one('joomla.easydiscuss.post', joomla_column=True)
    tag_ids = fields.Many2many('joomla.easydiscuss.tag', joomla_relation='discuss_posts_tags',
                               joomla_column1='post_id', joomla_column2='tag_id')
    attachment_ids = fields.One2many('joomla.easydiscuss.attachment', 'post_id')
    sef_url = fields.Char(compute='_compute_sef_url')
    odoo_id = fields.Many2one('forum.post')

    @api.depends('language', 'category_id.language')
    def _compute_language(self):
        for post in self:
            language = self._get_lang_from_code(post.language)
            if not language:
                language = self._get_lang_from_code(post.category_id.language)
            post.language_id = language

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
        tags = self.tag_ids.mapped('odoo_id')
        values.update(
            name=self.name if not self.parent_id else False,
            content=content,
            parent_id=self.parent_id.odoo_id.id,
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
            content = self.content
            for attachment in self.attachment_ids:
                code = '[attachment]{}[/attachment]'.format(attachment.name)
                if code not in content:
                    content += code
            html = parser.format(content)
        else:
            html = self.content
        return html

    def _create_image_block(self, url, title):
        return """
            <p>
                <img class="{}" src="{}" title="{}"
            </p>
        """.format(self.responsive_img_class, url, title)

    def _create_attachment_block(self, url, title):
        return """
            <p>
                <a href="{}" class="o_image" title="{}"
            </p>
        """.format(url, title)

    def _bbcode_render_attachment(self, tag_name, value, options, parent, context):
        self.ensure_one()
        for attachment in self.attachment_ids:
            if attachment.name == value and attachment.odoo_id:
                url = attachment.odoo_id.get_image_url()
                if url:
                    return self._create_image_block(url, value)
                url = attachment.odoo_id.get_content_url()
                if url:
                    return self._create_attachment_block(url, value)
        return ''

    def _bbcode_render_img(self, tag_name, value, options, parent, context):
        self.ensure_one()
        url = self._migrate_image(value)
        if url:
            return self._create_image_block(url, '')
        return ''

    def _get_bbcode_parser(self):
        self.ensure_one()
        parser = bbcode.Parser(replace_links=False)
        parser.add_formatter('img', self._bbcode_render_img)
        parser.add_formatter('attachment', self._bbcode_render_attachment)
        parser.add_simple_formatter('code', '<pre>%(value)s</pre>', transform_newlines=False)
        # TODO: add formatters for some video sites such as youtube,...
        parser.add_simple_formatter('video', ' %(value)s ')
        return parser

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_forum_post_values()
        user = self.user_id.odoo_id.user_ids[:1] or self._get_default_user()
        post = self.env(user=user.id)['forum.post'].with_context(mail_create_nolog=True).create(values)
        self._add_url_map(self.sef_url, post.sef_url)
        return post

    def post_migrate(self):
        for idx, post in enumerate(self, start=1):
            self._logger.info('[{}/{}] updating log access for forum post {}'.format(idx, len(self), post.alias))
            if post.odoo_id:
                sql = "UPDATE forum_post SET create_date = %s, write_date = %s, write_uid = %s WHERE id = %s"
                self._cr.execute(sql, (post.created, post.modified_date, post.user_id.odoo_id.id, post.odoo_id.id))
                self._cr.commit()
