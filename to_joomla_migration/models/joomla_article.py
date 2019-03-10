import json

from odoo import api, fields, models
from .abstract_j_model import _is_lang_code


class JoomlaArticle(models.TransientModel):
    _name = 'joomla.article'
    _description = 'Joomla Article'
    _inherit = 'abstract.j.model'
    _joomla_table = 'content'

    name = fields.Char(joomla_column='title')
    alias = fields.Char(joomla_column=True)
    author_id = fields.Many2one('joomla.user', joomla_column='created_by')
    introtext = fields.Text(joomla_column=True)
    fulltext = fields.Text(joomla_column=True)
    images = fields.Text(joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    publish_up = fields.Datetime(joomla_column=True)
    state = fields.Integer(joomla_column=True)
    category_id = fields.Many2one('joomla.category', joomla_column='catid')
    category_ids = fields.Many2many('joomla.category',
                                    compute='_compute_categories')
    language = fields.Char(joomla_column=True)
    metakey = fields.Text(joomla_column=True)
    metadesc = fields.Text(joomla_column=True)
    ordering = fields.Integer(joomla_column=True)
    tag_ids = fields.Many2many('joomla.tag', compute='_compute_tags')
    menu_ids = fields.One2many('joomla.menu', 'article_id')
    sef_url = fields.Char(index=True)
    intro_image_url = fields.Char(compute='_compute_intro_image_url', store=True)
    odoo_page_id = fields.Many2one('website.page')
    odoo_blog_post_id = fields.Many2one('blog.post')
    odoo_compat_lang_id = fields.Many2one('res.lang')

    def _compute_categories(self):
        for article in self:
            categories = self.env['joomla.category']
            cat = article.category_id
            while cat:
                categories += cat
                cat = cat.parent_id
            article.category_ids = categories

    @api.depends('images')
    def _compute_intro_image_url(self):
        for article in self:
            try:
                url = json.loads(article.images).get('image_intro', False)
                if url and not url.startswith('/'):
                    url = '/' + url
                article.intro_image_url = url
            except json.JSONDecodeError:
                pass

    def _compute_tags(self):
        for article in self:
            article.tag_ids = self.env['joomla.article.tag'].search(
                [('article_id', '=', article.id)]).mapped('tag_id')

    @api.model
    def _done(self):
        super(JoomlaArticle, self)._done()
        articles = self.search([])
        articles._compute_language()
        articles._compute_url()

    def _compute_language(self):
        for article in self:
            if not _is_lang_code(article.language) and article.menu_ids:
                menu = article.menu_ids[0]
                while menu.parent_id:
                    if _is_lang_code(menu.language):
                        article.language = menu.language
                        break
                    menu = menu.parent_id
            if not _is_lang_code(article.language):
                for category in article.category_ids:
                    if _is_lang_code(category.language):
                        article.language = category.language
                        break
            compat_lang = article.get_odoo_lang(article.language)
            if compat_lang:
                article.odoo_compat_lang_id = compat_lang.id

    def _compute_url(self):
        """
        Ref: https://docs.joomla.org/Special:MyLanguage/Search_Engine_Friendly_URLs
        """
        for article in self:
            url = False
            if article.menu_ids:
                url = '/' + article.menu_ids[0].path
            else:
                url_category_segments = []
                for category in article.category_ids[:-1]:
                    if not category.menu_ids:
                        seg = '{}-{}'.format(category.joomla_id, category.alias)
                        url_category_segments.append(seg)
                        continue
                    menu = category.menu_ids[0]
                    seg = '{}-{}'.format(article.joomla_id, article.alias)
                    url_segments = [menu.path, *url_category_segments, seg]
                    url = '/' + '/'.join(url_segments)
                    break
            if not url:
                continue
            if _is_lang_code(article.language):
                url = '/' + article.language[:2] + url
            article.sef_url = url

