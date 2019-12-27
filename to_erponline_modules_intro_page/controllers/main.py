import math

from odoo import http


class ModulesIntro(http.Controller):

    @http.route(['/intro/modules'], type='http', auth='public', website=True)
    def intro_modules(self, page=None):
        try:
            page = int(page)
        except:
            page = 1
        values = self._prepare_intro_modules_page_values(page)
        return http.request.render('to_erponline_modules_intro_page.modules_intro', values)

    def _prepare_intro_modules_page_values(self, page):
        lang = http.request.lang
        if lang == 'vi_VN':
            prefix = '/gioi-thieu/tinh-nang/cac-phan-he/'
        else:
            prefix = '/intro/modules/'
        Page = http.request.env['website.page']
        domain = [('url', '=like', '{}%'.format(prefix))]
        module_pages_count = Page.search_count(domain)
        amount_per_page = 10
        number_of_pages = math.ceil(module_pages_count / amount_per_page)
        if page < 1 or page > number_of_pages:
            page = 1
        module_pages = http.request.env['website.page'].search(domain, offset=(page - 1) * amount_per_page, limit=amount_per_page)
        values = dict(
            module_pages=module_pages,
            number_of_pages=number_of_pages,
            page=page,
        )
        return values
