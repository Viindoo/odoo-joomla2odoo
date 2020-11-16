from odoo import models, tools

class Website(models.Model):
    _inherit = 'website'
    
    def _compute_menu(self):
        self.env['website.menu'].clear_caches()
        return super(Website, self)._compute_menu()
    
    @tools.ormcache('self.env.uid', 'self.id')
    def _get_menu_ids(self):
        return super(Website, self.with_context(search_from_website=True))._get_menu_ids()

