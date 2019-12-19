import urllib.parse

from odoo import api, fields, models


class JoomlaMenu(models.TransientModel):
    _name = 'joomla.menu'
    _description = 'Joomla Menu'
    _inherit = 'abstract.joomla.model'
    _joomla_table = 'menu'

    parent_id = fields.Many2one('joomla.menu', joomla_column=True)
    path = fields.Char(joomla_column=True)
    link = fields.Char(joomla_column=True)
    language = fields.Char(joomla_column=True)
    article_id = fields.Many2one('joomla.article')
    category_id = fields.Many2one('joomla.category')
    easyblog = fields.Boolean()

    def _post_load_data(self):
        super(JoomlaMenu, self)._post_load_data()
        self._compute_params()

    def _compute_params(self):
        for menu in self:
            url_components = urllib.parse.urlparse(menu.link)
            if not url_components.path == 'index.php':
                continue
            query = dict(urllib.parse.parse_qsl(url_components.query))
            option = query.get('option')
            view = query.get('view')
            jid = int(query.get('id', False))
            if option == 'com_content' and jid:
                if view == 'article':
                    menu.article = self.env['joomla.article'].search([('joomla_id', '=', jid)], limit=1)
                elif view in ['category', 'categories']:
                    menu.category = self.env['joomla.category'].search([('joomla_id', '=', jid)], limit=1)
            elif option == 'com_easyblog' and view == 'latest':
                menu.easyblog = True
