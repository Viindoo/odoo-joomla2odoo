import json
import re
import urllib.parse

from odoo import api, fields, models


class EasyBlogPost(models.TransientModel):
    _name = 'joomla.easyblog.post'
    _inherit = 'abstract.joomla.content'
    _description = 'EasyBlog Post'
    _joomla_table = 'easyblog_post'

    name = fields.Char(joomla_column='title')
    permalink = fields.Char(joomla_column=True)
    author_id = fields.Many2one('joomla.user', joomla_column='created_by')
    intro = fields.Text(joomla_column=True)
    content = fields.Text(joomla_column=True)
    image = fields.Text(joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    published = fields.Integer(joomla_column=True)
    publish_up = fields.Datetime(joomla_column=True)
    state = fields.Integer(joomla_column=True)
    language = fields.Char(joomla_column=True, string='Language Code')
    language_id = fields.Many2one('res.lang', compute='_compute_language')
    meta_ids = fields.One2many('joomla.easyblog.meta', 'content_id')
    tag_ids = fields.Many2many('joomla.easyblog.tag', joomla_relation='easyblog_post_tag',
                               joomla_column1='post_id', joomla_column2='tag_id')
    url = fields.Char(compute='_compute_url')
    sef_url = fields.Char(compute='_compute_url')
    intro_image_url = fields.Char(compute='_compute_intro_image_url')
    odoo_id = fields.Many2one('blog.post')

    @api.depends('image')
    def _compute_intro_image_url(self):
        for post in self:
            if not post.image:
                post.intro_image_url = False
            elif post.image.startswith('shared/'):
                post.intro_image_url = '/images/easyblog_shared/' + post.image[7:]
            elif post.image.startswith('user:'):
                post.intro_image_url = '/images/easyblog_images/' + post.image[5:]

    @api.depends('language')
    def _compute_language(self):
        menu = self.env['joomla.menu'].search([('easyblog', '=', True)], limit=1)
        for post in self:
            language = self._get_lang_from_code(post.language)
            if not language and menu:
                language = self._get_lang_from_code(menu.language)
            post.language_id = language

    @api.depends('language_id', 'permalink')
    def _compute_url(self):
        for post in self:
            if post.language_id:
                url = '/{}/blog'.format(post.language_id.code[:2])
            else:
                url = '/blog'
            post.url = '{}?view=entry&id={}'.format(url, post.joomla_id)
            post.sef_url = '{}/entry/{}'.format(url, post.permalink)

    def _migrate_html(self, html, to_xml=False):
        html = self._convert_embed_video_code(html)
        return super(EasyBlogPost, self)._migrate_html(html, to_xml)

    def _convert_embed_video_code(self, content):
        matches = re.finditer(r'\[embed=videolink\](.*)\[/embed\]', content)
        code_map = {}
        for match in matches:
            code = match.group(1)
            meta = json.loads(code)
            video_url = meta.get('video')
            width, height = meta.get('width'), meta.get('height')
            url_components = urllib.parse.urlparse(video_url)
            if not url_components.netloc.endswith('youtube.com'):
                continue
            queries = urllib.parse.parse_qs(url_components.query)
            video_id = queries.get('v')
            if not video_id:
                continue
            video_id = video_id[0]
            new_code = """
                <iframe width="{}" height="{}"
                    src="https://www.youtube.com/embed/{}"
                    frameborder="0" allowfullscreen>
                </iframe>""".format(width, height, video_id)
            code_map[match.group(0)] = new_code
        for old_code, new_code in code_map.items():
            content = content.replace(old_code, new_code)
        return content

    def _prepare_blog_post_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        author = self.author_id.odoo_id.partner_id or self._get_default_partner()
        content = self._prepare_blog_post_content(self.intro + self.content, self.intro_image_url)
        meta = self.meta_ids.filtered(lambda r: r.type == 'post')
        tags = self.tag_ids.mapped('odoo_blog_tag_id')
        values.update(
            name=self.name,
            author_id=author.id,
            content=content,
            tag_ids=[(6, 0, tags.ids)],
            post_date=self.publish_up or self.created,
            active=self.state == 0,
            website_published=self.published == 1,
            website_meta_keywords=meta.keywords,
            website_meta_description=meta.description,
            language_id=self.language_id.id,
            blog_id=self.migration_id.to_blog_id.id
        )
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_blog_post_values()
        post = self.env['blog.post'].create(values)
        self._add_url_map(post.sef_url, self.sef_url, redirect=False)
        self._add_url_map(post.sef_url, self.sef_url)
        return post
