# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    website_id = fields.Many2one('website')
