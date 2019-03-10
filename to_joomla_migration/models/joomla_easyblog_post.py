import json
import re
import urllib.parse

from odoo import api, fields, models
from .abstract_j_model import _is_lang_code


class EasyBlogPost(models.TransientModel):
    _name = 'joomla.easyblog.post'
    _description = 'EasyBlog Post'
    _inherit = 'abstract.j.model'
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
    language = fields.Char(joomla_column=True)
    meta_ids = fields.One2many('joomla.easyblog.meta', 'content_id')
    tag_ids = fields.Many2many('joomla.easyblog.tag', compute='_compute_tags')
    url = fields.Char(index=True)
    sef_url = fields.Char(index=True)
    intro_image_url = fields.Char(compute='_compute_intro_image_url', store=True)
    odoo_blog_post_id = fields.Many2one('blog.post')
    odoo_compat_lang_id = fields.Many2one('res.lang')

    def _compute_tags(self):
        for post in self:
            post.tag_ids = self.env['joomla.easyblog.post.tag'].search(
                [('post_id', '=', post.id)]).mapped('tag_id')

    @api.depends('image')
    def _compute_intro_image_url(self):
        for post in self:
            if not post.image:
                continue
            elif post.image.startswith('shared/'):
                post.intro_image_url = '/images/easyblog_shared/' + post.image[7:]
            elif post.image.startswith('user:'):
                post.intro_image_url = '/images/easyblog_images/' + post.image[5:]

    @api.model
    def _done(self):
        super(EasyBlogPost, self)._done()
        posts = self.search([])
        posts._compute_language()
        posts._compute_url()
        posts._convert_embed_video_code()

    def _compute_language(self):
        for post in self:
            if not _is_lang_code(post.language):
                menu = self.env['joomla.menu'].search(
                    [('easyblog', '=', True)], limit=1)
                if menu and _is_lang_code(menu.language):
                    post.language = menu.language
            compat_lang = post.get_odoo_lang(post.language)
            if compat_lang:
                post.odoo_compat_lang_id = compat_lang.id

    def _compute_url(self):
        for post in self:
            if _is_lang_code(post.language):
                url = '/{}/blog'.format(post.language[:2])
            else:
                url = '/blog'
            post.url = '{}?view=entry&id={}'.format(url, post.joomla_id)
            post.sef_url = '{}/entry/{}'.format(url, post.permalink)

    def _convert_embed_video_code(self):
        for post in self:
            content = post.content
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
            post.content = content

