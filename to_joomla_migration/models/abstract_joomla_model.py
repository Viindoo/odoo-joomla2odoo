import base64
import logging
import urllib.parse

import requests

from odoo import fields, models, api, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import ormcache


class AbstractJoomlaModel(models.AbstractModel):
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
    _name = 'abstract.joomla.model'
    _description = 'Abstract Joomla Model'
    _joomla_table = False

    joomla_id = fields.Integer(joomla_column='id', index=True, help='ID of the origin record in Joomla')
    migration_id = fields.Many2one('joomla.migration', required=True, ondelete='cascade')
    m2o_info = fields.Text(help='Store info about origin references of many2one fields in Joomla for resolving after loading data')

    @property
    def _logger(self):
        return logging.getLogger(self._name)

    def search(self, args, offset=0, limit=None, order=None, count=False):
        migration = self._get_current_migration()
        if migration:
            args = expression.AND([args, [('migration_id', '=', migration.id)]])
        return super(AbstractJoomlaModel, self).search(args, offset, limit, order, count)

    def _post_load_data(self):
        """ Executed after all models are loaded and relational fields are resolved """
        pass

    def _prepare_track_values(self):
        self.ensure_one()
        return {
            'migration_id': self.migration_id.id,
            'old_website': self.migration_id.website_url,
            'old_website_model': self._get_jtable_fullname(),
            'old_website_record_id': self.joomla_id
        }

    def _get_jtable_fullname(self):
        migration = self[:1].migration_id or self._get_current_migration()
        return migration._get_jtable_fullname(self._joomla_table)

    def _get_current_migration(self):
        return self.env['joomla.migration'].get_current_migration()

    def _get_lang_from_code(self, code):
        lang = self.env['res.lang']
        if code:
            lang_id = self._get_lang_id_from_code(code)
            lang = lang.browse(lang_id)
        return lang

    @ormcache('code')
    def _get_lang_id_from_code(self, code):
        lang = self.env['res.lang']
        code = code.replace('-', '_')
        all_langs = lang.search([])
        exact_matches = all_langs.filtered(lambda r: r.code == code)
        if exact_matches:
            lang = exact_matches[0]
        else:
            nearest_matches = all_langs.filtered(lambda r: r.code.startswith(code[:2]))
            if nearest_matches:
                lang = nearest_matches[0]
        return lang.id

    def _get_default_user(self):
        return self.env['res.users'].browse(SUPERUSER_ID)

    def _get_default_partner(self):
        return self._get_default_user().partner_id

    def _download_file(self, url):
        if not url:
            return None
        absolute_url = urllib.parse.urljoin(self.migration_id.website_url, url)
        self._logger.info('downloading {}'.format(absolute_url))
        try:
            return requests.get(absolute_url).content
        except Exception as e:
            self._logger.warning('failed to download {}\n'.format(absolute_url, e))
            return None

    def _prepare_attachment_values(self, name, data_b64):
        self.ensure_one()
        values = self._prepare_track_values()
        values.update(
            name=name,
            datas=data_b64,
            datas_fname=name,
            res_model='ir.ui.view',
            public=True,
            website_id=self.migration_id.to_website_id.id
        )
        return values

    def _migrate_attachment(self, download_url, name=None):
        self.ensure_one()
        attachment = self.env['ir.attachment']
        data = self._download_file(download_url)
        if not data:
            return attachment
        data_b64 = base64.b64encode(data)
        if not name:
            name = download_url.rsplit('/', maxsplit=1)[-1]
        values = self._prepare_attachment_values(name, data_b64)
        attachment = attachment.create(values)
        return attachment

    def _get_matching_data(self, odoo_model):
        return self._get_matching_data_by_track(odoo_model)

    def _get_matching_data_by_track(self, odoo_model):
        try:
            data = self.env[odoo_model].get_migrated_data(jtable=self._get_jtable_fullname())
        except AttributeError:
            return {}
        id_map1 = {r.old_website_record_id: r for r in data}
        id_map2 = {r: r.joomla_id for r in self.search([])}
        return {r: id_map1[_id] for r, _id in id_map2.items() if _id in id_map1}

    def _get_matching_data_by_name(self, odoo_model):
        return self._get_matching_data_by_field(odoo_model, 'name', 'name')

    def _get_matching_data_by_field(self, odoo_model, j_field_name, o_field_name):
        map1 = {r[o_field_name]: r for r in self.env[odoo_model].search([])}
        map2 = {r: r[j_field_name] for r in self.search([])}
        return {r: map1[field] for r, field in map2.items() if field in map1}

    def _migrate(self):
        return False

    @api.noguess
    def migrate(self, *args, result_field='odoo_id', meth='_migrate', **kwargs):
        field = self._fields[result_field]
        data = self._get_matching_data(field.comodel_name)
        for idx, record in enumerate(self, start=1):
            self._logger.info('[{}/{}] migrating {}'.format(idx, len(self), record.display_name))
            result = data.get(record, self.env[field.comodel_name])
            if not result:
                result = getattr(record, meth)(*args, **kwargs)
            record[result_field] = result
            self._cr.commit()
