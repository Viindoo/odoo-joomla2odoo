# -*- coding: utf-8 -*-
import base64
import logging
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime

import lxml.etree
import lxml.html

from odoo import _, api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import html_sanitize

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
    redirect = fields.Boolean(default=False)

    to_website_id = fields.Many2one('website', default=_default_to_website)
    to_blog_id = fields.Many2one('blog.blog', default=_default_to_blog)

    user_ids = fields.One2many('joomla.user', 'migration_id')
    category_ids = fields.One2many('joomla.category', 'migration_id')
    article_ids = fields.One2many('joomla.article', 'migration_id')
    easyblog_post_ids = fields.One2many('joomla.easyblog.post', 'migration_id')

    user_mapping_ids = fields.One2many('joomla.migration.user.mapping', 'migration_id')
    article_mapping_ids = fields.One2many('joomla.migration.article.mapping', 'migration_id')

    migrating_info = fields.Text()
    no_reset_password = fields.Boolean(string='No Reset Password', default=True, help="If checked, no reset password request will be raised")

    @api.constrains('website_url')
    def _check_website_url(self):
        if not re.match(r'https?://[a-zA-Z0-9.\-:]+$', self.website_url):
            message = _('Invalid website URL!. Website URL should be like '
                        'http[s]://your.domain')
            raise ValidationError(message)

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
        self = self.with_context(active_test=False)
        old_data = self.env['joomla.migration'].search([]) - self
        old_data.unlink()

        _logger.info('start loading data')
        if not self._load_data():
            raise UserError(_('No data to migrate!'))
        if self.include_user:
            self._init_user_mapping()
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

    def _load_data(self):
        joomla_models = self._registered_joomla_models()
        for model in joomla_models:
            self.env[model]._load_data(self)
            _logger.info('loaded {}'.format(model))
        for model in joomla_models:
            self.env[model]._resolve_m2o_fields()
            _logger.info('resolved m2o fields in {}'.format(model))
        for model in joomla_models:
            self.env[model]._done()
        return joomla_models

    def _registered_joomla_models(self):
        joomla_models = []
        if self.include_user:
            joomla_models.extend(['joomla.user'])
        if self.include_article:
            joomla_models.extend(['joomla.category', 'joomla.article',
                                  'joomla.tag', 'joomla.article.tag'])
        if self.include_easyblog:
            joomla_models.extend(['joomla.easyblog.post', 'joomla.easyblog.meta',
                                  'joomla.easyblog.tag', 'joomla.easyblog.post.tag'])
        if self.include_article or self.include_easyblog:
            joomla_models.extend(['joomla.menu'])
        return joomla_models

    def _init_user_mapping(self):
        odoo_users = self.env['res.users'].search([])
        email_map_user = {r.email: r for r in odoo_users}
        for joomla_user in self.user_ids:
            odoo_user = email_map_user.get(joomla_user.email)
            if odoo_user:
                self.env['joomla.migration.user.mapping'].create({
                    'migration_id': self.id,
                    'joomla_user_id': joomla_user.id,
                    'odoo_user_id': odoo_user.id
                })

    def _get_migrating_info(self):
        info = 'Found data:\n'
        if self.include_user:
            info += '- {} users\n'.format(len(self.user_ids))
        if self.include_article:
            info += '- {} articles\n'.format(len(self.article_ids))
        if self.include_easyblog:
            info += '- {} easyblog posts\n'.format(len(self.easyblog_post_ids))
        return info

    def migrate_data(self):
        self.ensure_one()
        self = self.with_context(active_test=False)
        _logger.info('start migrating data')
        start = datetime.now()
        request.url_map = {}
        self._migrate_data()
        self._update_href()
        if self.redirect:
            self._create_redirects()
        time = datetime.now() - start
        _logger.info('migrating completed ({}m, {}s)'
                     .format(time.seconds // 60, time.seconds % 60))

    def _migrate_data(self):
        if self.include_user:
            _logger.info('migrating users')
            self._migrate_users()
        if self.include_article:
            _logger.info('migrating articles')
            self._migrate_articles()
        if self.include_easyblog:
            _logger.info('migrating easyblog')
            self._migrate_easyblog_tags()
            self._migrate_easyblog()

    def _migrate_users(self):
        ResUser = self.env['res.users']
        ResPartner = self.env['res.partner']

        partners = ResPartner.search([])
        email_partners = defaultdict(list)
        for partner in partners:
            if partner.email:
                email_partners[partner.email].append(partner)

        existing_users = ResUser.search([])
        existing_login_names = {user.login for user in existing_users}
        user_mapping = {r.joomla_user_id: r.odoo_user_id for r in self.user_mapping_ids}
        portal_group = self.env.ref('base.group_portal')

        for idx, joomla_user in enumerate(self.user_ids, start=1):
            _logger.info('[{}/{}] migrating user {}'
                         .format(idx, len(self.user_ids), joomla_user.username))
            existing_partner = False
            existing_user = user_mapping.get(joomla_user)
            if not existing_user:
                partners = email_partners.get(joomla_user.email)
                if partners and len(partners) == 1:
                    existing_partner = partners[0]
            if not existing_user:
                login = joomla_user.username
                if login in existing_login_names:
                    login = joomla_user.email
                if login in existing_login_names:
                    _logger.info('ignore')
                    continue
                values = {
                    'name': joomla_user.name,
                    'groups_id': [(4, portal_group.id)],
                    'login': login,
                    'email': joomla_user.email,
                    'active': not joomla_user.block,
                    'migration_id': self.id,
                    'old_website': self.website_url,
                    'old_website_model': 'users',
                    'old_website_record_id': joomla_user.joomla_id,
                    'website_id': self.to_website_id.id,
                }
                if existing_partner:
                    values.update(partner_id=existing_partner.id,
                                  created_from_existing_partner=True)
                if self.no_reset_password:
                    existing_user = ResUser.with_context(no_reset_password=True).create(values)
                else:
                    existing_user = ResUser.create(values)
                if existing_partner:
                    _logger.info('created new user from existing partner')
                else:
                    _logger.info('created new user')
            else:
                _logger.info('found matching user')
            joomla_user.odoo_user_id = existing_user.id

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
            _logger.info('[{}/{}] migrating page {}'
                         .format(idx, total, article.alias))
            self._migrate_article_to_page(article)

        total = len(blog_articles)
        for idx, article in enumerate(blog_articles, start=1):
            _logger.info('[{}/{}] migrating blog post {}'
                         .format(idx, total, article.alias))
            self._migrate_article_to_blog_post(article)

    def _migrate_article_to_page(self, article):
        content = article.introtext + article.fulltext
        content = self._convert_content_common(content, 'xml')
        intro_image_url = self._migrate_image(article.intro_image_url)
        view = self._build_page_view(article.name, content, intro_image_url)
        category_path = slugify(article.category_id.path, path=True)
        page_url = '/' + category_path + '/' + slugify(article.alias)
        page_values = {
            'name': article.name,
            'url': page_url,
            'view_id': view.id,
            'website_published': article.state == 1,
            'website_ids': [(4, self.to_website_id.id)],
            'active': article.state == 0 or article.state == 1,
            'language_id': article.odoo_compat_lang_id.id,
            'migration_id': self.id,
            'old_website': self.website_url,
            'old_website_model': 'article',
            'old_website_record_id': article.joomla_id,
            'website_id': self.to_website_id.id
        }
        page = self.env['website.page'].create(page_values)
        article.odoo_page_id = page.id
        if article.sef_url:
            request.url_map[article.sef_url] = page.sef_url
        return page

    def _build_page_view(self, name, content, intro_image_url=None):
        if intro_image_url:
            content = """
                <p>
                    <img src="{}" class="center-block img-responsive"/>
                </p>
            """.format(intro_image_url) + content
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
        """.format(slugify(name), content)
        view_values = {
            'name': name,
            'type': 'qweb',
            'arch_base': view_arch
        }
        return self.env['ir.ui.view'].create(view_values)

    def _migrate_article_to_blog_post(self, article):
        content = article.introtext + article.fulltext
        content = self._convert_content_common(content)
        intro_image_url = self._migrate_image(article.intro_image_url)
        content = self._build_blog_post_content(content, intro_image_url)
        author = article.author_id.odoo_user_id.partner_id
        if not author:
            author = self.env.user.partner_id
        self._migrate_article_tag_to_blog_tag(article)
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
            'tag_ids': [(6, 0, tags.ids)],
            'language_id': article.odoo_compat_lang_id.id,
            'migration_id': self.id,
            'old_website': self.website_url,
            'old_website_model': 'article',
            'old_website_record_id': article.joomla_id
        }
        post = self.env['blog.post'].create(post_values)
        article.odoo_blog_post_id = post.id
        if article.sef_url:
            request.url_map[article.sef_url] = post.sef_url
        return post

    def _migrate_article_tag_to_blog_tag(self, article):
        blog_tags = self.env['blog.tag'].search([])
        blog_tag_names = {r.name: r for r in blog_tags}
        for tag in article.tag_ids:
            if tag.odoo_blog_tag_id:
                continue
            blog_tag = blog_tag_names.get(tag.name)
            if not blog_tag:
                values = {
                    'name': tag.name,
                    'migration_id': self.id
                }
                blog_tag = self.env['blog.tag'].create(values)
            tag.odoo_blog_tag_id = blog_tag.id

    def _migrate_easyblog(self):
        posts = self.easyblog_post_ids
        total = len(posts)
        for idx, post in enumerate(posts, start=1):
            _logger.info('[{}/{}] migrating blog post {}'
                         .format(idx, total, post.permalink))
            self._migrate_easyblog_post(post)

    def _migrate_easyblog_post(self, post):
        content = post.intro + post.content
        content = self._convert_content_common(content)
        intro_image_url = self._migrate_image(post.intro_image_url)
        content = self._build_blog_post_content(content, intro_image_url)
        author = post.author_id.odoo_user_id.partner_id
        meta = post.meta_ids.filtered(lambda r: r.type == 'post')
        if not author:
            author = self.env.user.partner_id
        tags = post.tag_ids.mapped('odoo_blog_tag_id')
        post_values = {
            'blog_id': self.to_blog_id.id,
            'name': post.name,
            'author_id': author.id,
            'content': content,
            'website_published': post.published == 1,
            'post_date': post.publish_up or post.created,
            'active': post.state == 0,
            'website_meta_keywords': meta.keywords,
            'website_meta_description': meta.description,
            'tag_ids': [(6, 0, tags.ids)],
            'language_id': post.odoo_compat_lang_id.id,
            'migration_id': self.id,
            'old_website': self.website_url,
            'old_website_model': 'easyblog_post',
            'old_website_record_id': post.joomla_id
        }
        new_post = self.env['blog.post'].create(post_values)
        post.odoo_blog_post_id = new_post.id
        if post.sef_url:
            request.url_map[post.sef_url] = new_post.sef_url
        return new_post

    @staticmethod
    def _build_blog_post_content(content, intro_image_url=None):
        if intro_image_url:
            content = """
                <p>
                    <img src="{}" class="center-block img-responsive"/>
                </p>
            """.format(intro_image_url) + content
        content = """
            <section class="s_text_block">
                <div class="container">
                    {}
                </div>
            </section>
        """.format(content)
        return content

    def _migrate_easyblog_tags(self):
        odoo_tags = self.env['blog.tag'].search([])
        odoo_tag_names = {r.name: r for r in odoo_tags}
        easyblog_tags = self.env['joomla.easyblog.tag'].search([])
        for tag in easyblog_tags:
            odoo_tag = odoo_tag_names.get(tag.name)
            if not odoo_tag:
                values = {
                    'name': tag.name,
                    'migration_id': self.id
                }
                odoo_tag = self.env['blog.tag'].create(values)
            tag.odoo_blog_tag_id = odoo_tag.id

    def _convert_content_common(self, content, to='html'):
        if not content:
            return ''
        clean_content = html_sanitize(content)
        et = lxml.html.fromstring(clean_content)

        # convert image urls
        img_tags = et.findall('.//img')
        for img in img_tags:
            url = img.get('src')
            if url:
                new_url = self._migrate_image(url)
                img.set('src', new_url)
                img.classes.add('img-responsive')

        return lxml.html.tostring(et, encoding='unicode', method=to)

    def _migrate_image(self, image_url):
        if not image_url:
            return None
        if not self._is_internal_url(image_url):
            return image_url

        if '%' not in image_url:
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
            'public': True,
            'migration_id': self.id,
            'website_id': self.to_website_id.id
        }
        attach = self.env['ir.attachment'].create(values)
        new_url = '/web/image/{}/{}'.format(attach.id, name)
        return new_url

    def _update_href(self):
        this_migration = [('migration_id', '=', self.id)]

        new_pages = self.env['website.page'].search(this_migration)
        for idx, page in enumerate(new_pages, start=1):
            _logger.info('[{}/{}] updating href in page {}'
                         .format(idx, len(new_pages), page.name))
            content = self._update_href_for_content(page.view_id.arch_base, 'xml')
            page.view_id.arch_base = content

        new_posts = self.env['blog.post'].search(this_migration)
        for idx, post in enumerate(new_posts, start=1):
            _logger.info('[{}/{}] updating href in blog post {}'
                         .format(idx, len(new_posts), post.name))
            content = self._update_href_for_content(post.content)
            post.content = content

    def _update_href_for_content(self, content, to='html'):
        et = lxml.html.fromstring(content)
        a_tags = et.findall('.//a')
        for a in a_tags:
            url = a.get('href')
            if url and (url.startswith('mailto:') or url.startswith('#')):
                continue
            if url and self._is_internal_url(url):
                url = urllib.parse.urlparse(url).path
                if '%' in url:
                    url = urllib.parse.unquote(url)
                if not url.startswith('/'):
                    url = '/' + url
                new_url = request.url_map.get(url)
                if not new_url:
                    a.drop_tag()
                    _logger.info('dropped href {}'.format(url))
                else:
                    a.set('href', new_url)
                    _logger.info('converted href from {} to {}'.format(url, new_url))
        return lxml.html.tostring(et, encoding='unicode', method=to)

    def _is_internal_url(self, url):
        url_com = urllib.parse.urlparse(url)
        if not url_com.netloc:
            return True
        website_url_com = urllib.parse.urlparse(self.website_url)
        return url_com.netloc == website_url_com.netloc

    def _create_redirects(self):
        from_domain = urllib.parse.urlparse(self.website_url).hostname
        from_website = self.env['website'].search(
            [('domain', '=', from_domain)], limit=1)
        if not from_website:
            values = {
                'name': from_domain,
                'domain': from_domain
            }
            from_website = self.env['website'].create(values)
        to_website_url = self._get_website_url(self.to_website_id)
        for from_url, to_url in request.url_map.items():
            to_url = urllib.parse.urljoin(to_website_url, to_url)
            values = {
                'type': '301',
                'url_from': from_url,
                'url_to': to_url,
                'website_id': from_website.id,
                'migration_id': self.id
            }
            self.env['website.redirect'].create(values)

    @staticmethod
    def _get_website_url(website):
        request_url = request.httprequest.url_root
        request_url_components = urllib.parse.urlparse(request_url)
        url = '{}://{}'.format(request_url_components.scheme, website.domain)
        if request_url_components.port:
            url += ':{}'.format(request_url_components.port)
        return url

    def reset(self):
        self.ensure_one()
        self = self.with_context(active_test=False)
        created_by_migration = ('migration_id', '!=', False)

        _logger.info('removing website pages')
        pages = self.env['website.page'].search([created_by_migration])
        views = pages.mapped('view_id')
        pages.unlink()
        views.unlink()

        _logger.info('removing blog data')
        self.env['blog.post'].search([created_by_migration]).unlink()
        self.env['blog.tag'].search([created_by_migration]).unlink()

        _logger.info('removing image attachments')
        self.env['ir.attachment'].search([created_by_migration]).unlink()

        _logger.info('removing users')
        users = self.env['res.users'].search([created_by_migration])
        partners = users.filtered(
            lambda r: not r.created_from_existing_partner).mapped('partner_id')
        users.unlink()
        partners.unlink()

        _logger.info('removing redirects')
        self.env['website.redirect'].search([created_by_migration]).unlink()


class UserMapping(models.TransientModel):
    _name = 'joomla.migration.user.mapping'
    _description = 'User Migration Mapping'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    joomla_user_id = fields.Many2one('joomla.user')
    odoo_user_id = fields.Many2one('res.users')


class ArticleMapping(models.TransientModel):
    _name = 'joomla.migration.article.mapping'
    _description = 'Article Migration Mapping'

    migration_id = fields.Many2one('joomla.migration', ondelete='cascade')
    category_id = fields.Many2one('joomla.category', required=True)
    migrate_to = fields.Selection([('page', 'Page'), ('blog', 'Blog')],
                                  required=True, default='page')
