# -*- coding: utf-8 -*-
import werkzeug.utils

from odoo import api, fields, models, _
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        website = request.env['website'].get_current_website()
        request.website = website
        redirect = cls._serve_redirect()
        if redirect:
            return werkzeug.utils.redirect(redirect.url_to, int(redirect.type))
        return super(IrHttp, cls)._dispatch()
