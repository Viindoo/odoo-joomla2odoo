from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    def _default_pricelist_vnd(self):
        return self.env['product.pricelist'].browse(1).exists()

    def _default_pricelist_usd(self):
        return self.env['product.pricelist'].browse(3).exists()

    website_url = fields.Char(default='http://erponline.vn')
    db_table_prefix = fields.Char(default='lgzds_')
    include_article = fields.Boolean(default=True)
    include_easydiscuss = fields.Boolean(default=True)
    include_erpmanager = fields.Boolean(default=True)
    redirect = fields.Boolean(default=True)
    pricelist_vnd_id = fields.Many2one('product.pricelist', default=_default_pricelist_vnd)
    pricelist_usd_id = fields.Many2one('product.pricelist', default=_default_pricelist_usd)

    def _load_data(self):
        res = super(JoomlaMigration, self)._load_data()
        if self.include_article:
            self._init_article_map()
        return res

    def _init_article_map(self):
        category_ids = [2, 11, 13, 29, 39, 41, 80, 98]
        categories = self.category_ids.filtered(lambda c: c.joomla_id in category_ids)
        for cat in categories:
            self.article_map_ids.create(dict(
                migration_id=self.id,
                category_id=cat.id,
                migrate_to='page'
            ))
