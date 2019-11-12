import json
import logging

from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify

_logger = logging.getLogger(__name__)


class JoomlaArticle(models.TransientModel):
    _name = 'joomla.article'
    _description = 'Joomla Article'
    _inherit = 'abstract.joomla.content'
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
    category_ids = fields.Many2many('joomla.category', string='Categories', compute='_compute_categories')
    language = fields.Char(joomla_column=True, string='Language Code')
    metakey = fields.Text(joomla_column=True)
    metadesc = fields.Text(joomla_column=True)
    ordering = fields.Integer(joomla_column=True)
    tag_ids = fields.Many2many('joomla.tag', compute='_compute_tags')
    menu_ids = fields.One2many('joomla.menu', 'article_id')
    sef_url = fields.Char(index=True)
    intro_image_url = fields.Char(compute='_compute_intro_image_url', store=True)
    website_page_id = fields.Many2one('website.page')
    blog_post_id = fields.Many2one('blog.post')
    language_id = fields.Many2one('res.lang')

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
        article_tag = self.env['joomla.article.tag'].search([('article_id', 'in', self.ids)])
        for article in self:
            article.tag_ids = article_tag.filtered(lambda at: at.article_id == article).mapped('tag_id')

    @api.model
    def _post_load_data(self):
        super(JoomlaArticle, self)._post_load_data()
        articles = self.search([])
        articles._compute_language()
        articles._compute_sef_url()

    def _compute_language(self):
        for article in self:
            if not self._is_lang_code(article.language) and article.menu_ids:
                menu = article.menu_ids[0]
                while menu.parent_id:
                    if self._is_lang_code(menu.language):
                        article.language = menu.language
                        break
                    menu = menu.parent_id
            if not self._is_lang_code(article.language):
                for category in article.category_ids:
                    if self._is_lang_code(category.language):
                        article.language = category.language
                        break
            article.language_id = self._get_lang_from_code(article.language)

    def _compute_sef_url(self):
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
            if self._is_lang_code(article.language):
                url = '/' + article.language[:2] + url
            article.sef_url = url

    def _prepare_website_page_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        category_path = slugify(self.category_id.path, path=True)
        url = '/' + category_path + '/' + slugify(self.alias)
        view_values = self._prepare_website_page_view_values()
        view = self.env['ir.ui.view'].create(view_values)
        values.update(
            name=self.name,
            url=url,
            view_id=view.id,
            website_published=self.state == 1,
            website_id=self.migration_id.to_website_id.id,
            website_ids=[(4, self.migration_id.to_website_id.id)],
            active=self.state == 0 or self.state == 1,
            language_id=self.language_id.id
        )
        return values

    def _prepare_website_page_view_values(self):
        self.ensure_one()
        content = self.introtext + self.fulltext
        content = self._migrate_html(content, to_xml=True)
        if self.intro_image_url:
            intro_image_url = self._migrate_image(self.intro_image_url)
            content = """
                <p>
                    <img src="{}" class="center-block {}"/>
                </p>
            """.format(intro_image_url, self.responsive_img_class) + content
        view_arch = """
            <t t-name="website.{}">
                <t t-call="website.layout">
                    <div id="wrap" class="oe_structure oe_empty">
                        <div class="container">
                            {}
                        </div>
                    </div>
                </t>
            </t>
        """.format(slugify(self.name), content)
        values = dict(
            name=self.name,
            type='qweb',
            arch_base=view_arch
        )
        return values

    def _migrate_to_website_page(self):
        self.ensure_one()
        values = self._prepare_website_page_values()
        self.website_page_id = self.env['website.page'].create(values)
        self._add_url_map(self.sef_url, self.website_page_id.sef_url)

    def migrate_to_website_page(self):
        migrated_data_map = self.env['website.page'].get_migrated_data_map()
        for idx, article in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating page {}'.format(idx, len(self), article.alias))
            if article.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                article.website_page_id = migrated_data_map[article.joomla_id]
            else:
                article._migrate_to_website_page()

    def _prepare_blog_post_values(self):
        self.ensure_one()
        values = self._prepare_track_values()
        author = self.author_id.odoo_user_id.partner_id or self._get_default_partner()
        content = self._prepare_blog_post_content(self.introtext + self.fulltext, self.intro_image_url)
        tags = self.tag_ids.mapped('blog_tag_id')
        values.update(
            name=self.name,
            author_id=author.id,
            content=content,
            tag_ids=[(6, 0, tags.ids)],
            website_published=self.state == 1,
            website_meta_keywords=self.metakey,
            website_meta_description=self.metadesc,
            post_date=self.publish_up or self.created,
            language_id=self.language_id.id,
            blog_id=self.migration_id.to_blog_id.id
        )
        return values

    def _migrate_to_blog_post(self):
        self.ensure_one()
        values = self._prepare_blog_post_values()
        self.blog_post_id = self.env['blog.post'].create(values)
        self._add_url_map(self.sef_url, self.blog_post_id.sef_url)

    def migrate_to_blog_post(self):
        migrated_data_map = self.env['blog.post'].get_migrated_data_map()
        for idx, article in enumerate(self, start=1):
            _logger.info('[{}/{}] migrating blog post {}'.format(idx, len(self), article.alias))
            if article.joomla_id in migrated_data_map:
                _logger.info('ignore, already migrated')
                article.blog_post_id = migrated_data_map[article.joomla_id]
            else:
                article._migrate_to_blog_post()
