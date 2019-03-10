from odoo import api, fields, models


class JoomlaUser(models.TransientModel):
    _name = 'joomla.user'
    _description = 'Joomla User'
    _inherit = 'abstract.j.model'
    _joomla_table = 'users'

    name = fields.Char(joomla_column=True)
    username = fields.Char(joomla_column=True)
    email = fields.Char(joomla_column=True)
    block = fields.Boolean(joomla_column=True)
    odoo_user_id = fields.Many2one('res.users')
    params = fields.Char(joomla_column=True)
