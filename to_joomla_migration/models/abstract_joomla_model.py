import base64
import json
import logging
import urllib.parse

import mysql.connector
import requests

from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import ormcache

_logger = logging.getLogger(__name__)


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

    joomla_id = fields.Integer(joomla_column='id', index=True)
    migration_id = fields.Many2one('joomla.migration', required=True, ondelete='cascade')
    m2o_joomla_ids = fields.Text()

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
        if 'id' in field_map:
            query += " ORDER BY id"
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
    def _post_load_data(self):
        """
        Executed after all models are loaded and m2o fields are resolved.
        """
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
        migration = self[0].migration_id or self._get_current_migration()
        return migration.db_table_prefix + self._joomla_table

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
        active_lang = lang.search([('active', '=', True)])
        exact_matches = active_lang.filtered(lambda r: r.code == code)
        if exact_matches:
            lang = exact_matches[0]
        else:
            nearest_matches = active_lang.filtered(lambda r: r.code.startswith(code[:2]))
            if nearest_matches:
                lang = nearest_matches[0]
        return lang.id

    def _is_lang_code(self, code):
        return code and self._get_lang_id_from_code(code)

    def _get_default_user(self):
        return self.env['res.users'].browse(SUPERUSER_ID)

    def _get_default_partner(self):
        return self._get_default_user().partner_id

    def _download_file(self, url):
        if not url:
            return None
        absolute_url = urllib.parse.urljoin(self.migration_id.website_url, url)
        _logger.info('downloading {}'.format(absolute_url))
        try:
            return requests.get(absolute_url).content
        except Exception as e:
            _logger.warning('failed to download {}\n'.format(absolute_url, e))
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
        data = self._download_file(download_url)
        if not data:
            return None
        data_b64 = base64.b64encode(data)
        if not name:
            name = download_url.rsplit('/', maxsplit=1)[-1]
        values = self._prepare_attachment_values(name, data_b64)
        attachment = self.env['ir.attachment'].create(values)
        return attachment
