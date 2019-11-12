import base64
import logging
import re
import urllib.parse
import urllib.request
from datetime import datetime
from operator import itemgetter

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class JoomlaMigration(models.TransientModel):
    _name = 'joomla.migration'
    _description = 'Joomla Migration'

    def _default_to_website(self):
        return self.env['website'].search([], limit=1)

    def _default_to_blog(self):
        return self.env['blog.blog'].search([], limit=1)

    def _default_to_forum(self):
        return self.env['forum.forum'].search([], limit=1)

    website_url = fields.Char(required=True)
    host_address = fields.Char(required=True, default='localhost')
    host_port = fields.Integer(required=True, default=3306)
    db_user = fields.Char(required=True)
    db_password = fields.Char(required=True)
    db_name = fields.Char(required=True)
    db_table_prefix = fields.Char()

    to_website_id = fields.Many2one('website', default=_default_to_website)
    to_blog_id = fields.Many2one('blog.blog', default=_default_to_blog)
    to_forum_id = fields.Many2one('forum.forum', default=_default_to_forum)

    state = fields.Selection([('setup', 'Setup'), ('migrating', 'Migrating')], default='setup')
    migrating_info = fields.Text()

    @api.constrains('website_url')
    def _check_website_url(self):
        if not re.match(r'https?://[a-zA-Z0-9.\-:]+$', self.website_url):
            message = _('Invalid website URL!. Website URL should be like http[s]://your.domain')
            raise ValidationError(message)

    @api.model
    def default_get(self, fields_list):
        # Restore last setup info
        values = super(JoomlaMigration, self).default_get(fields_list)
        last = self.env['joomla.migration'].search([], limit=1, order='id desc')
        if last:
            last_values = last.copy_data()[0]
            values.update(last_values)
        return values

    def _get_window_action(self):
        self.ensure_one()
        action = self.env.ref('to_joomla_migration.open_migration_view')
        values = action.read()[0]
        values.update(res_id=self.id)
        return values

    def load_data(self):
        self.ensure_one()
        old_data = self.env['joomla.migration'].search([('id', '!=', self.id)])
        old_data.unlink()

        _logger.info('loading data...')
        if not self.with_context(active_test=False)._load_data():
            raise UserError(_('No data to migrate!'))
        _logger.info('loaded data')

        self.state = 'migrating'
        self.migrating_info = self._get_migrating_info()

        return self._get_window_action()

    def _load_data(self):
        items = self.get_joomla_models()
        items = sorted(items.items(), key=itemgetter(1))
        jmodels = list(item[0] for item in items)
        for model in jmodels:
            _logger.info('loading {}...'.format(model))
            self.env[model]._load_data(self)
        for model in jmodels:
            _logger.info('resolving m2o fields of {}...'.format(model))
            self.env[model]._resolve_m2o_fields()
        for model in jmodels:
            self.env[model]._post_load_data()
        return jmodels

    def _get_migrating_info(self):
        info = []
        for model in self.get_joomla_models():
            Model = self.env[model]
            count = Model.search([('migration_id', '=', self.id)], count=True)
            info.append('{:<6} {}'.format(count, Model._description))
        info = '\n'.join(info)
        return info

    def get_joomla_models(self):
        # return {model: sequence}
        return {}

    def migrate_data(self):
        self.ensure_one()
        _logger.info('migrating data...')
        start = datetime.now()
        self.with_context(active_test=False, joomla_migration=self)._migrate_data()
        self.with_context(active_test=False)._post_migrate_data()
        time = datetime.now() - start
        _logger.info('migrated data ({}m, {}s)'.format(time.seconds // 60, time.seconds % 60))

    def get_current_migration(self):
        return self._context.get('joomla_migration', self.browse())

    def _migrate_data(self):
        pass

    def _post_migrate_data(self):
        pass

    def back(self):
        self.ensure_one()
        for model in self.get_joomla_models():
            self.env[model].with_context(active_test=False).search([]).unlink()
        self.state = 'setup'
        return self._get_window_action()

    def reset(self):
        self.ensure_one()
        items = self._get_records_to_reset()
        items = sorted(items, key=itemgetter(1))
        for item in items:
            item[0].unlink()
        return self._get_window_action()

    def _get_records_to_reset(self):
        # return [(records, sequence)]
        attachments = self.env['ir.attachment'].get_migrated_data()
        return [(attachments, 1000)]
