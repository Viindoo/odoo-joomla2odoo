import odoo.addons.http_routing.models.ir_http as ir_http

slugify_one = ir_http.slugify_one
translation_table = str.maketrans({'đ': 'd', 'Đ': 'd'})


def slugify_one_plus(s, *args, **kwargs):
    s = s.translate(translation_table)
    return slugify_one(s, *args, **kwargs)


ir_http.slugify_one = slugify_one_plus


def post_init_hook(cr, reg):
    ir_http.slugify_one = slugify_one_plus


def uninstall_hook(cr, reg):
    ir_http.slugify_one = slugify_one
