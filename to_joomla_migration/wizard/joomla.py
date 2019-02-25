# -*- coding: utf-8 -*-
import json
import re
import urllib.parse

import mysql.connector

from odoo import api, fields, models, _
from odoo.exceptions import UserError


def _is_lang_code(s):
    return s and '-' in s


def _find_odoo_compat_lang(env, lang):
    if not _is_lang_code(lang):
        return False
    lang = lang.replace('-', '_')
    active_lang = env['res.lang'].search([('active', '=', True)])
    exact_matches = active_lang.filtered(lambda r: r.code == lang)
    if exact_matches:
        return exact_matches[0]
    nearest_matches = active_lang.filtered(lambda r: r.code.startswith(lang[:2]))
    if nearest_matches:
        return nearest_matches[0]
    return False


class JoomlaModel(models.AbstractModel):
    """
    This is base model for models that map to corresponding joomla database
    tables for easier to play with.

    Model attributes:
        _joomla_table: name of the corresponding joomla database table.

    Field attributes:
        joomla_column: use this attribute if you want to map the field to a
            column in the corresponding joomla database table. Value should be
            name of the corresponding column or True if the field name is
            exactly the column name.
    """
    _name = 'joomla.model'
    _description = 'Joomla Model Base Class'
    _joomla_table = None

    joomla_id = fields.Integer(joomla_column='id', index=True)
    migration_id = fields.Many2one('joomla.migration', required=True,
                                   ondelete='cascade')
    m2o_joomla_ids = fields.Char()

    @api.model
    def _load_data(self, migration):
        try:
            connection = mysql.connector.connect(
                host=migration.host_address,
                port=migration.host_port,
                user=migration.db_user,
                password=migration.db_password,
                database=migration.db_name)
        except mysql.connector.Error as e:
            raise UserError(e.msg)

        try:
            cursor = connection.cursor()
            query = self._prepare_select_query(migration)
            cursor.execute(query)
            column_names = cursor.column_names
            rows = cursor.fetchall()
        except mysql.connector.Error as e:
            raise UserError(e.msg)
        finally:
            connection.close()

        for row in rows:
            values = dict(zip(column_names, row))
            for k in values:
                if isinstance(values[k], bytearray):
                    values[k] = values[k].decode()
            m2o_joomla_ids = {}
            for k in list(values):
                if k.startswith('joomla_') and k != 'joomla_id':
                    m2o_joomla_ids[k[7:]] = values.pop(k)
            values.update(migration_id=migration.id,
                          m2o_joomla_ids=json.dumps(m2o_joomla_ids))
            self.create(values)

    @api.model
    def _prepare_select_query(self, migration):
        table = self._joomla_table
        assert isinstance(table, str)
        if migration.db_table_prefix:
            table = migration.db_table_prefix + table

        field_map = {}  # field -> field alias
        for field in self._fields.values():
            joomla_column = field._attrs.get('joomla_column')
            if not joomla_column:
                continue
            alias = field.name
            if field.type == 'many2one':
                alias = 'joomla_' + alias
            if joomla_column is True:
                field_map[field.name] = alias
            elif isinstance(joomla_column, str):
                field_map[joomla_column] = alias

        select_expr = []
        for name, alias in field_map.items():
            if name == alias:
                select_expr.append('`{}`'.format(name))
            else:
                select_expr.append('`{}` as `{}`'.format(name, alias))

        select_expr_s = ', '.join(select_expr)
        query = """SELECT {} FROM {}""".format(select_expr_s, table)
        return query

    @api.model
    def _resolve_m2o_fields(self):
        m2o_joomla_fields = []
        for field in self._fields.values():
            if field.type == 'many2one' and field._attrs.get('joomla_column'):
                m2o_joomla_fields.append(field)

        if not m2o_joomla_fields:
            return

        records = self.search([])
        for r in records:
            values = {}
            m2o_joomla_ids = json.loads(r.m2o_joomla_ids)
            for field in m2o_joomla_fields:
                domain = [('joomla_id', '=', m2o_joomla_ids[field.name])]
                ref = self.env[field.comodel_name].search(domain, limit=1)
                values[field.name] = ref.id
            r.write(values)

    @api.model
    def _done(self):
        """
        Executed after all models are loaded and m2o fields are resolved.
        """
        pass


class JoomlaUser(models.TransientModel):
    _name = 'joomla.user'
    _description = 'Joomla User'
    _inherit = 'joomla.model'
    _joomla_table = 'users'

    name = fields.Char(joomla_column=True)
    username = fields.Char(joomla_column=True)
    email = fields.Char(joomla_column=True)
    block = fields.Boolean(joomla_column=True)
    odoo_user_id = fields.Many2one('res.users')


class JoomlaCategory(models.TransientModel):
    _name = 'joomla.category'
    _description = 'Joomla Category'
    _inherit = 'joomla.model'
    _joomla_table = 'categories'

    name = fields.Char(joomla_column='title')
    alias = fields.Char(joomla_column=True)
    path = fields.Char(joomla_column=True)
    language = fields.Char(joomla_column=True)
    parent_id = fields.Many2one('joomla.category', joomla_column=True)
    menu_ids = fields.One2many('joomla.menu', 'category_id')
    extension = fields.Char(joomla_column=True)


class JoomlaArticle(models.TransientModel):
    _name = 'joomla.article'
    _description = 'Joomla Article'
    _inherit = 'joomla.model'
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
            compat_lang = _find_odoo_compat_lang(self.env, article.language)
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


class JoomlaTag(models.TransientModel):
    _name = 'joomla.tag'
    _description = 'Joomla Tag'
    _inherit = 'joomla.model'
    _joomla_table = 'tags'

    name = fields.Char(joomla_column='title')
    odoo_blog_tag_id = fields.Many2one('blog.tag')


class JoomlaArticleTag(models.TransientModel):
    _name = 'joomla.article.tag'
    _description = 'Joomla Article Tag'
    _inherit = 'joomla.model'
    _joomla_table = 'contentitem_tag_map'

    joomla_id = False
    article_id = fields.Many2one('joomla.article', joomla_column='content_item_id')
    tag_id = fields.Many2one('joomla.tag', joomla_column=True)


class JoomlaMenu(models.TransientModel):
    _name = 'joomla.menu'
    _description = 'Joomla Menu'
    _inherit = 'joomla.model'
    _joomla_table = 'menu'

    parent_id = fields.Many2one('joomla.menu', joomla_column=True)
    path = fields.Char(joomla_column=True)
    link = fields.Char(joomla_column=True)
    language = fields.Char(joomla_column=True)
    article_id = fields.Many2one('joomla.article')
    category_id = fields.Many2one('joomla.category')
    easyblog = fields.Boolean()

    @api.model
    def _resolve_m2o_fields(self):
        super(JoomlaMenu, self)._resolve_m2o_fields()
        self.search([])._compute_params()

    def _compute_params(self):
        for menu in self:
            url_components = urllib.parse.urlparse(menu.link)
            if not url_components.path == 'index.php':
                continue
            query = dict(urllib.parse.parse_qsl(url_components.query))
            option = query.get('option')
            view = query.get('view')
            jid = int(query.get('id', False))
            if option == 'com_content' and jid:
                if view == 'article':
                    menu.article_id = self.env['joomla.article'].search(
                        [('joomla_id', '=', jid)], limit=1).id
                elif view in ['category', 'categories']:
                    menu.category_id = self.env['joomla.category'].search(
                        [('joomla_id', '=', jid)], limit=1).id
            elif option == 'com_easyblog' and view == 'latest':
                menu.easyblog = True


class EasyBlogPost(models.TransientModel):
    _name = 'joomla.easyblog.post'
    _description = 'EasyBlog Post'
    _inherit = 'joomla.model'
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
            compat_lang = _find_odoo_compat_lang(self.env, post.language)
            if compat_lang:
                post.odoo_compat_lang_id = compat_lang.id

    def _compute_url(self):
        for post in self:
            url = '/blog/entry/' + post.permalink
            if _is_lang_code(post.language):
                url = '/' + post.language[:2] + url
            post.sef_url = url

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


class EasyBlogMeta(models.TransientModel):
    _name = 'joomla.easyblog.meta'
    _description = 'EasyBlog Meta'
    _inherit = 'joomla.model'
    _joomla_table = 'easyblog_meta'

    type = fields.Char(joomla_column=True)
    content_id = fields.Many2one('joomla.easyblog.post', joomla_column=True)
    keywords = fields.Text(joomla_column=True)
    description = fields.Text(joomla_column=True)


class EasyBlogTag(models.TransientModel):
    _name = 'joomla.easyblog.tag'
    _description = 'EasyBlog Tag'
    _inherit = 'joomla.model'
    _joomla_table = 'easyblog_tag'

    name = fields.Char(joomla_column='title')
    odoo_blog_tag_id = fields.Many2one('blog.tag')


class EasyBlogPostTag(models.TransientModel):
    _name = 'joomla.easyblog.post.tag'
    _description = 'EasyBlog Post Tag'
    _inherit = 'joomla.model'
    _joomla_table = 'easyblog_post_tag'

    joomla_id = False
    tag_id = fields.Many2one('joomla.easyblog.tag', joomla_column=True)
    post_id = fields.Many2one('joomla.easyblog.post', joomla_column=True)
