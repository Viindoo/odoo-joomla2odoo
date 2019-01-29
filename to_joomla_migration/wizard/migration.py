# -*- coding: utf-8 -*-
import base64
import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import datetime
from json import JSONDecodeError

import lxml.html
import mysql.connector

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _name = 'joomla.migration'
    _description = 'Joomla Migration'

    def _default_to_website(self):
        return self.env['website'].search([], limit=1).id

    def _default_to_blog(self):
        return self.env['blog.blog'].search([], limit=1).id

    website_url = fields.Char(required=True)
    host_address = fields.Char(required=True, default='localhost')
    host_port = fields.Integer(required=True, default=3306)
    db_user = fields.Char(required=True)
    db_password = fields.Char(required=True)
    db_name = fields.Char(required=True)
    db_table_prefix = fields.Char()

    state = fields.Selection([('setup', 'Setup'), ('migrating', 'Migrating')],
                             default='setup')

    include_user = fields.Boolean(default=True)
    include_article = fields.Boolean(default=True)
    include_easyblog = fields.Boolean(default=False)

    to_website_id = fields.Many2one('website', default=_default_to_website)
    to_blog_id = fields.Many2one('blog.blog', default=_default_to_blog)

    user_ids = fields.One2many('joomla.user', 'migration_id')
    category_ids = fields.One2many('joomla.category', 'migration_id')
    article_ids = fields.One2many('joomla.article', 'migration_id')
    easyblog_post_ids = fields.One2many('joomla.easyblog.post', 'migration_id')

    user_mapping_ids = fields.One2many('joomla.migration.user.mapping', 'migration_id')
    article_mapping_ids = fields.One2many('joomla.migration.article.mapping', 'migration_id')

    migrating_info = fields.Text()

    @api.onchange('website_url')
    def _onchange_website_url(self):
        if not self.website_url:
            return
        if not re.match(r'https?://\w', self.website_url):
            raise UserError(_('Invalid website URL!. Website URL should be like '
                              'http[s]://your.domain'))

    @api.model
    def default_get(self, fields_list):
        # Restore last setup info
        values = super(JoomlaMigration, self).default_get(fields_list)
        last = self.env['joomla.migration'].search([], limit=1, order='id desc')
        if last:
            last_values = last.read(['website_url', 'host_address', 'host_port',
                                     'db_user', 'db_password', 'db_name',
                                     'db_table_prefix'])[0]
            values.update(last_values)
        return values

    def load_data(self):
        self.ensure_one()
        self._remove_old_data()

        _logger.info('start loading data')
        if not self._load_data():
            raise UserError(_('No data to migrate!'))
        if self.include_user:
            self._initialize_user_mapping()
        _logger.info('loading completed')

        self.state = 'migrating'
        self.migrating_info = self._get_migrating_info()

        return {
            'name': 'Joomla Migration',
            'type': 'ir.actions.act_window',
            'res_model': 'joomla.migration',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _remove_old_data(self):
        # Remove old data to avoid slowing down
        old = self.env['joomla.migration'].search([]) - self
        old.unlink()

    def _get_migrating_info(self):
        info = 'Found data:\n'
        if self.include_user:
            info += '- {} users\n'.format(len(self.user_ids))
        if self.include_article:
            info += '- {} articles\n'.format(len(self.article_ids))
        if self.include_easyblog:
            info += '- {} easyblog posts\n'.format(len(self.easyblog_post_ids))
        return info

    def _load_data(self):
        joomla_models = self._get_joomla_models()
        for model in joomla_models:
            self._import_joomla_model(model)
            _logger.info('imported {}'.format(model))
        for model in joomla_models:
            self._sync_id(model)
        return joomla_models

    def _initialize_user_mapping(self):
        odoo_users = self.env['res.users'].with_context(active_test=False).search([])
        email_map_user = {r.email: r for r in odoo_users}
        for joomla_user in self.user_ids:
            odoo_user = email_map_user.get(joomla_user.email)
            if odoo_user:
                self.env['joomla.migration.user.mapping'].create({
                    'migration_id': self.id,
                    'joomla_user_id': joomla_user.id,
                    'odoo_user_id': odoo_user.id
                })

    def _get_joomla_models(self):
        joomla_models = []
        if self.include_user:
            joomla_models.extend(['joomla.user'])
        if self.include_article:
            joomla_models.extend(['joomla.category', 'joomla.article',
                                  'joomla.tag', 'joomla.article.tag'])
        if self.include_easyblog:
            joomla_models.extend(['joomla.easyblog.post', 'joomla.easyblog.meta',
                                  'joomla.easyblog.tag', 'joomla.easyblog.post.tag'])
        return joomla_models

    def _import_joomla_model(self, model):
        JModel = self.env[model]

        try:
            connection = mysql.connector.connect(
                host=self.host_address, port=self.host_port,
                user=self.db_user, password=self.db_password,
                database=self.db_name)
        except mysql.connector.Error as e:
            raise UserError(e.msg)

        try:
            cursor = connection.cursor()
            query = self._prepare_select_query(model)
            cursor.execute(query)
            column_names = cursor.column_names
            rows = cursor.fetchall()
        finally:
            connection.close()

        JModel.search([('migration_id', '=', self.id)]).unlink()
        for row in rows:
            values = dict(zip(column_names, row))
            values.update(migration_id=self.id)
            JModel.create(values)

    def _prepare_select_query(self, model):
        JModel = self.env[model]
        table = self.db_table_prefix + JModel._joomla_table

        field_map = {}  # odoo field name -> joomla field name
        for field in JModel._fields.values():
            joomla_column = field._attrs.get('joomla_column')
            if not joomla_column:
                continue
            if joomla_column is True:
                field_map[field.name] = field.name
            elif isinstance(joomla_column, str):
                field_map[field.name] = joomla_column

        select_expr = []
        for odoo_field, joomla_field in field_map.items():
            if odoo_field == joomla_field:
                select_expr.append('`{}`'.format(joomla_field))
            else:
                select_expr.append('`{}` as `{}`'.format(joomla_field, odoo_field))

        select_expr_s = ', '.join(select_expr)
        query = """SELECT {} FROM {}""".format(select_expr_s, table)
        return query

    def _sync_id(self, model):
        """
        Compute odoo id based on corresponding joomla id.

        Mapping between joomla id field and odoo id field is determined
        by naming convention, example: x_joomla_id -> x_id
        """
        JModel = self.env[model]
        field_map = {}  # joomla field -> joomla field
        for field in JModel._fields.values():
            if field.name.endswith('_joomla_id'):
                joomla_field = field
                odoo_name = field.name.replace('joomla_id', 'id')
                if odoo_name in JModel._fields:
                    odoo_field = JModel._fields[odoo_name]
                    field_map[joomla_field] = odoo_field

        if not field_map:
            return

        records = JModel.search([])
        for r in records:
            values = {}
            for joomla_field, odoo_field in field_map.items():
                domain = [('migration_id', '=', r.migration_id.id),
                          ('joomla_id', '=', getattr(r, joomla_field.name))]
                comodel = self.env[odoo_field.comodel_name]
                record = comodel.search(domain, limit=1)
                values[odoo_field.name] = record.id
            r.write(values)

    def migrate_data(self):
        self.ensure_one()
        _logger.info('start migrating data')
        start = datetime.now()
        self._migrate_data()
        time = datetime.now() - start
        _logger.info('migrating completed ({}m, {}s)'
                     .format(time.seconds // 60, time.seconds % 60))

    def _migrate_data(self):
        if self.include_user:
            _logger.info('migrating users')
            self._migrate_users()
        if self.include_article:
            _logger.info('migrating articles')
            self._migrate_article_tags()
            self._migrate_articles()
        if self.include_easyblog:
            _logger.info('migrating easyblog')
            self._migrate_easyblog_tags()
            self._migrate_easyblog()

    def _migrate_users(self):
        ResUser = self.env['res.users']
        odoo_users = ResUser.with_context(active_test=False).search([])
        email_map_user = {user.email: user for user in odoo_users}
        login_names = {user.login for user in odoo_users}
        user_map = {r.joomla_user_id: r.odoo_user_id for r in self.user_mapping_ids}
        total = len(self.user_ids)
        portal_group = self.env.ref('base.group_portal')
        for idx, joomla_user in enumerate(self.user_ids, start=1):
            odoo_user = user_map.get(joomla_user) or email_map_user.get(joomla_user.email)
            if not odoo_user:
                login = joomla_user.username
                if login in login_names:
                    login = joomla_user.email
                values = {
                    'name': joomla_user.name,
                    'groups_id': [(4, portal_group.id)],
                    'login': login,
                    'email': joomla_user.email,
                    'active': not joomla_user.block
                }
                odoo_user = ResUser.create(values)
                _logger.info('[{}/{}] created user {}'
                             .format(idx, total, joomla_user.username))
            joomla_user.odoo_user_id = odoo_user.id

    def _migrate_articles(self):
        articles = self.article_ids
        page_articles = blog_articles = self.env['joomla.article']

        for m in self.article_mapping_ids:
            records = articles.filtered(
                lambda r: m.category_id in r.category_ids
            )
            if m.migrate_to == 'page':
                page_articles |= records
            elif m.migrate_to == 'blog':
                blog_articles |= records
            articles -= records

        total = len(page_articles)
        for idx, article in enumerate(page_articles, start=1):
            self._article_to_page(article.id)
            _logger.info('[{}/{}] created page {}'
                         .format(idx, total, article.alias))

        total = len(blog_articles)
        for idx, article in enumerate(blog_articles, start=1):
            self._article_to_blog_post(article.id)
            _logger.info('[{}/{}] created blog post {}'
                         .format(idx, total, article.alias))

    def _migrate_easyblog(self):
        posts = self.easyblog_post_ids
        total = len(posts)
        for idx, post in enumerate(posts, start=1):
            self._convert_easyblog_post(post.id)
            _logger.info('[{}/{}] created blog post {}'
                         .format(idx, total, post.permalink))

    def _convert_easyblog_post(self, e_post_id):
        e_post = self.env['joomla.easyblog.post'].browse(e_post_id)
        main_content = self._migrate_content(e_post.intro + e_post.content)
        if not e_post.image:
            intro_image_url = None
        elif e_post.image.startswith('shared/'):
            intro_image_url = 'images/easyblog_shared/' + e_post.image[7:]
        elif e_post.image.startswith('user:'):
            intro_image_url = 'images/easyblog_images/' + e_post.image[5:]
        else:
            intro_image_url = None
        intro_image_url = self._migrate_image(intro_image_url)
        content = self._construct_blog_post_content(main_content, intro_image_url)
        author = e_post.author_id.odoo_user_id.partner_id
        meta = e_post.meta_ids.filtered(lambda r: r.type == 'post')
        if not author:
            author = self.env.user.partner_id
        tags = e_post.tag_ids.mapped('odoo_blog_tag_id')
        post_values = {
            'blog_id': self.to_blog_id.id,
            'name': e_post.name,
            'author_id': author.id,
            'content': content,
            'website_published': e_post.published == 1,
            'post_date': e_post.publish_up or e_post.created,
            'active': e_post.state == 0,
            'website_meta_keywords': meta.keywords,
            'website_meta_description': meta.description,
            'tag_ids': [(6, 0, tags.ids)]
        }
        post = self.env['blog.post'].create(post_values)
        return post.id

    def _article_to_page(self, article_id):
        article = self.env['joomla.article'].browse(article_id)
        content = article.introtext + article.fulltext
        content = self._migrate_content(content, to='xml')
        view_arch = self._construct_page_view_template(article.alias, content)
        view_values = {
            'name': article.name,
            'type': 'qweb',
            'arch_base': view_arch
        }
        view = self.env['ir.ui.view'].create(view_values)
        page_url = '/' + article.category_id.path + article.alias
        page_values = {
            'name': article.name,
            'url': page_url,
            'view_id': view.id,
            'website_published': article.state == 1,
            'website_ids': [(4, self.to_website_id.id)],
            'active': article.state == 0 or article.state == 1
        }
        page = self.env['website.page'].create(page_values)
        return page.id

    @staticmethod
    def _construct_page_view_template(name, content):
        return """
            <t t-name="website.{}">
                <t t-call="website.layout">
                    <div id="wrap" class="oe_structure oe_empty">
                        {}
                    </div>
                </t>
            </t>
        """.format(name, content)

    def _article_to_blog_post(self, article_id):
        article = self.env['joomla.article'].browse(article_id)
        main_content = self._migrate_content(article.introtext + article.fulltext)
        try:
            images = json.loads(article.images)
        except JSONDecodeError:
            _logger.warning('failed to read images info')
            intro_image_url = None
        else:
            intro_image_url = images.get('image_intro')
            intro_image_url = self._migrate_image(intro_image_url)
        content = self._construct_blog_post_content(main_content, intro_image_url)
        author = article.author_id.odoo_user_id.partner_id
        if not author:
            author = self.env.user.partner_id
        tags = article.tag_ids.mapped('odoo_blog_tag_id')
        post_values = {
            'blog_id': self.to_blog_id.id,
            'name': article.name,
            'author_id': author.id,
            'content': content,
            'website_published': article.state == 1,
            'post_date': article.publish_up or article.created,
            'website_meta_keywords': article.metakey,
            'website_meta_description': article.metadesc,
            'tag_ids': [(6, 0, tags.ids)]
        }
        post = self.env['blog.post'].create(post_values)
        return post.id

    def _migrate_article_tags(self):
        odoo_tags = self.env['blog.tag'].search([])
        odoo_tag_names = {r.name: r for r in odoo_tags}
        article_tags = self.env['joomla.tag'].search([])
        for tag in article_tags:
            odoo_tag = odoo_tag_names.get(tag.name)
            if not odoo_tag:
                values = {
                    'name': tag.name
                }
                odoo_tag = self.env['blog.tag'].create(values)
            tag.odoo_blog_tag_id = odoo_tag.id

    def _migrate_easyblog_tags(self):
        odoo_tags = self.env['blog.tag'].search([])
        odoo_tag_names = {r.name: r for r in odoo_tags}
        easyblog_tags = self.env['joomla.easyblog.tag'].search([])
        for tag in easyblog_tags:
            odoo_tag = odoo_tag_names.get(tag.name)
            if not odoo_tag:
                values = {
                    'name': tag.name
                }
                odoo_tag = self.env['blog.tag'].create(values)
            tag.odoo_blog_tag_id = odoo_tag.id

    @staticmethod
    def _construct_blog_post_content(main_content, intro_image_url=None):
        content = """
            <section class="s_text_block">
                <div class="container">
                    {}
                </div>
            </section>
        """.format(main_content)
        if intro_image_url:
            image = """
                <p>
                    <img src="{}" class="center-block"/>
                </p>
            """.format(intro_image_url)
            content = image + content
        return content

    def _migrate_content(self, content, to='html'):
        if not content:
            return ''
        et = lxml.html.fromstring(content)

        # convert image urls
        img_tags = et.findall('.//img')
        for img in img_tags:
            url = img.get('src')
            if url:
                new_url = self._migrate_image(url)
                img.set('src', new_url)

        # rewrite internal links
        a_tags = et.findall('.//a')
        for a in a_tags:
            url = a.get('href')
            if url and self._is_internal_url(url):
                a.set('href', '/')
        return lxml.html.tostring(et, encoding='unicode', method=to)

    def _migrate_image(self, image_url):
        if not image_url:
            return None
        if not self._is_internal_url(image_url):
            return image_url

        image_url = urllib.parse.quote(image_url)
        absolute_url = urllib.parse.urljoin(self.website_url, image_url)
        try:
            _logger.info('downloading {}'.format(absolute_url))
            data = urllib.request.urlopen(absolute_url).read()
        except urllib.request.URLError:
            _logger.warning('failed to download {}'.format(absolute_url))
            return None

        name = image_url.rsplit('/', maxsplit=1)[-1]
        data_b64 = base64.b64encode(data)
        values = {
            'name': name,
            'datas': data_b64,
            'datas_fname': name,
            'res_model': 'ir.ui.view',
            'public': True
        }
        attach = self.env['ir.attachment'].create(values)
        new_url = '/web/image/{}/{}'.format(attach.id, name)
        return new_url

    def _is_internal_url(self, url):
        url_com = urllib.parse.urlparse(url)
        if not url_com.netloc:
            return True
        website_url_com = urllib.parse.urlparse(self.website_url)
        return url_com.netloc == website_url_com.netloc


class UserMapping(models.TransientModel):
    _name = 'joomla.migration.user.mapping'
    _description = 'User Migration Mapping'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    joomla_user_id = fields.Many2one('joomla.user', required=True)
    odoo_user_id = fields.Many2one('res.users', required=True)


class ArticleMapping(models.TransientModel):
    _name = 'joomla.migration.article.mapping'
    _description = 'Article Migration Mapping'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    category_id = fields.Many2one('joomla.category', required=True)
    migrate_to = fields.Selection([('page', 'Page'), ('blog', 'Blog')],
                                  required=True, default='page')
