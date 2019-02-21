# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    website_id = fields.Many2one(related='partner_id.website_id', store=True)
