import json
import mysql.connector

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


def _is_lang_code(s):
    return s and '-' in s


class AbstractJModel(models.AbstractModel):
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
    _name = 'abstract.j.model'
    _description = 'Joomla Model Base Class'
    _joomla_table = None

    joomla_id = fields.Integer(joomla_column='id', index=True)
    migration_id = fields.Many2one('wizard.joomla.migration', required=True,
                                   ondelete='cascade')
    m2o_joomla_ids = fields.Char()

    def get_odoo_lang(self, jlang=None):
        lang_id = False
        if jlang:
            lang = jlang.replace('-', '_')
            active_lang = self.env['res.lang'].search([('active', '=', True)])
            exact_matches = active_lang.filtered(lambda r: r.code == lang)
            if exact_matches:
                lang_id = exact_matches[0]
            if not lang_id:
                nearest_matches = active_lang.filtered(lambda r: r.code.startswith(lang[:2]))
                if nearest_matches:
                    lang_id = nearest_matches[0]
        if not lang_id:
            lang_id = self._context.get('default_lang_for_jitems', False)
        if not lang_id:
            raise ValidationError(_("Could not find an appropriate langage for the record '%s' of the model '%s'.") % (self.display_name, self._name))
        return lang_id

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

