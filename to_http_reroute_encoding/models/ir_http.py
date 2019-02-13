# -*- coding: utf-8 -*-
from werkzeug._compat import wsgi_encoding_dance

from odoo import api, fields, models, _


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def reroute(cls, path):
        path = wsgi_encoding_dance(path)
        return super(IrHttp, cls).reroute(path)
