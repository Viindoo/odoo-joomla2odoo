import json
import logging
import re
from datetime import datetime
from operator import itemgetter

import mysql.connector
from psycopg2.extras import execute_values

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class JoomlaMigration(models.TransientModel):
    _name = 'joomla.migration'
    _description = 'Joomla Migration'
    _rec_name = 'website_url'

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

    to_website_id = fields.Many2one('website', default=_default_to_website, required=True)
    to_blog_id = fields.Many2one('blog.blog', default=_default_to_blog, required=True)
    to_forum_id = fields.Many2one('forum.forum', default=_default_to_forum, required=True)

    state = fields.Selection([('setup', 'Setup'), ('migrating', 'Migrating')], default='setup')
    migrating_info = fields.Text()

    @property
    def _logger(self):
        return logging.getLogger(self._name)

    @api.constrains('website_url')
    def _check_website_url(self):
        if not re.match(r'https?://[a-zA-Z0-9.\-:]+$', self.website_url):
            message = _('Invalid website URL!. Website URL should be like http[s]://your.domain')
            raise ValidationError(message)

    def load_data(self):
        self._logger.info('loading data...')
        if not self.with_context(active_test=False)._load_data():
            raise UserError(_('No data to migrate!'))
        self._logger.info('loaded data')

        self.state = 'migrating'
        self.migrating_info = self._get_migrating_info()

    def _load_data(self):
        items = self._get_joomla_models()
        items = sorted(items.items(), key=itemgetter(1))
        jmodels = list(item[0] for item in items)
        for model in jmodels:
            self._logger.info('loading model {}...'.format(model))
            self._load_model_data(model)
        resolved_relations = set()
        for model in jmodels:
            self._logger.info('resolving relational fields of model {}...'.format(model))
            self._resolve_m2o_fields(model)
            self._resolve_m2m_fields(model, resolved_relations)
        for model in jmodels:
            self.env[model].search([])._post_load_data()
        return jmodels

    def _connect(self):
        try:
            return mysql.connector.connect(
                host=self.host_address,
                port=self.host_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name)
        except mysql.connector.Error as e:
            raise UserError(e.msg)

    def _get_data(self, query, row_dict=False):
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            column_names = cursor.column_names
            rows = cursor.fetchall()
        except mysql.connector.Error as e:
            raise UserError(e.msg)
        finally:
            connection.close()

        for row in rows:
            decoded_row = (v.decode() if isinstance(v, bytearray) else v for v in row)
            if row_dict:
                yield dict(zip(column_names, decoded_row))
            else:
                yield decoded_row

    def _load_model_data(self, jmodel):
        query = self._prepare_data_query(jmodel)
        data = self._get_data(query, row_dict=True)
        JModel = self.env[jmodel]
        for values in data:
            m2o_info = {}
            for k in list(values):
                if k.startswith('joomla_') and k != 'joomla_id':
                    m2o_info[k[7:]] = values.pop(k)
            values.update(migration_id=self.id, m2o_info=json.dumps(m2o_info))
            JModel.create(values)

    def _get_jtable_fullname(self, jtable):
        if self.db_table_prefix:
            return self.db_table_prefix + jtable
        return jtable

    def _prepare_data_query(self, jmodel):
        JModel = self.env[jmodel]
        table = JModel._joomla_table
        assert isinstance(table, str)
        table = self._get_jtable_fullname(table)

        field_map = {}  # field -> field alias
        for field in JModel._fields.values():
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

    def _resolve_m2o_fields(self, jmodel):
        JModel = self.env[jmodel]
        m2o_fields = []
        for field in JModel._fields.values():
            if field.type == 'many2one' and field._attrs.get('joomla_column'):
                m2o_fields.append(field)
        if not m2o_fields:
            return

        records = JModel.search([('migration_id', '=', self.id)])
        for r in records:
            values = {}
            m2o_info = json.loads(r.m2o_info)
            for field in m2o_fields:
                domain = [('joomla_id', '=', m2o_info[field.name])]
                ref = self.env[field.comodel_name].search(domain, limit=1)
                values[field.name] = ref.id
            r.write(values)

    def _resolve_m2m_fields(self, jmodel, resolved_relations):
        JModel = self.env[jmodel]
        for field in JModel._fields.values():
            if field.type == 'many2many':
                jrelation = field._attrs.get('joomla_relation')
                if jrelation and jrelation not in resolved_relations:
                    jcolumn1 = field._attrs['joomla_column1']
                    jcolumn2 = field._attrs['joomla_column2']
                    query = "SELECT {}, {} FROM {}".format(jcolumn1, jcolumn2, self._get_jtable_fullname(jrelation))
                    data = self._get_data(query)
                    JComodel = self.env[field.comodel_name]
                    column1_map = {r.joomla_id: r.id for r in JModel.search([('migration_id', '=', self.id)])}
                    column2_map = {r.joomla_id: r.id for r in JComodel.search([('migration_id', '=', self.id)])}
                    query = "INSERT INTO {} ({}, {}) VALUES %s".format(field.relation, field.column1, field.column2)
                    argslist = ((column1_map[c1], column2_map[c2]) for c1, c2 in data if c1 in column1_map and c2 in column2_map)
                    execute_values(self._cr._obj, query, argslist)
                    resolved_relations.add(jrelation)

    def _get_migrating_info(self):
        info = []
        for model in self._get_joomla_models():
            Model = self.env[model]
            count = Model.search([('migration_id', '=', self.id)], count=True)
            info.append('{:<6} {}'.format(count, Model._description))
        info = '\n'.join(info)
        return info

    def _get_joomla_models(self):
        # return {model: sequence}
        return {}

    def migrate_data(self):
        self._logger.info('migrating data...')
        start = datetime.now()
        self = self.sudo().with_context(active_test=False)
        self = self.with_context(joomla_migration=self)
        self._migrate_data()
        self._post_migrate_data()
        time = datetime.now() - start
        self._logger.info('migrated data ({}m, {}s)'.format(time.seconds // 60, time.seconds % 60))

    def get_current_migration(self):
        return self._context.get('joomla_migration', self.browse())

    def _migrate_data(self):
        pass

    def _post_migrate_data(self):
        pass

    def back(self):
        self.ensure_one()
        if self.state == 'migrating':
            self._unload_data()
            self.state = 'setup'

    def _unload_data(self):
        for model in self._get_joomla_models():
            self.env[model].search([]).unlink()