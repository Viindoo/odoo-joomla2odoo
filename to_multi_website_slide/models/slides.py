# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Channel(models.Model):
    _inherit = 'slide.channel'

    website_id = fields.Many2one('website')
