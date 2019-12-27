from odoo import models, fields
from odoo.exceptions import UserError


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_erpmanager = fields.Boolean()

    partner_ids = fields.One2many('erpmanager.partner', 'migration_id')
    saleorder_ids = fields.One2many('erpmanager.saleorder', 'migration_id')
    wallet_ids = fields.One2many('erpmanager.wallet', 'migration_id')
    plan_ids = fields.One2many('erpmanager.plan', 'migration_id')
    pserver_ids = fields.One2many('erpmanager.pserver', 'migration_id')
    ip_ids = fields.One2many('erpmanager.ip', 'migration_id')
    proxyserver_ids = fields.One2many('erpmanager.proxyserver', 'migration_id')
    pgsqlserver_ids = fields.One2many('erpmanager.pgsqlserver', 'migration_id')
    dnsserver_ids = fields.One2many('erpmanager.dnsserver', 'migration_id')
    erpserver_ids = fields.One2many('erpmanager.erpserver', 'migration_id')
    vserver_ids = fields.One2many('erpmanager.vserver', 'migration_id')
    instance_ids = fields.One2many('erpmanager.instance', 'migration_id')
    instanceperm_ids = fields.One2many('erpmanager.instanceperm', 'migration_id')
    port_ids = fields.One2many('erpmanager.port', 'migration_id')
    basedomain_ids = fields.One2many('erpmanager.basedomain', 'migration_id')
    subdomain_ids = fields.One2many('erpmanager.subdomain', 'migration_id')
    blockedsubdomain_ids = fields.One2many('erpmanager.blockedsubdomain', 'migration_id')
    customerdomain_ids = fields.One2many('erpmanager.customerdomain', 'migration_id')
    defaulterpconfig_ids = fields.One2many('erpmanager.defaulterpconfig', 'migration_id')
    erpconfig_ids = fields.One2many('erpmanager.erpconfig', 'migration_id')
    customerplan_ids = fields.One2many('erpmanager.customerplan', 'migration_id')
    instance_history_ids = fields.One2many('erpmanager.instance.history', 'migration_id')
    instance_history_split_ids = fields.One2many('erpmanager.instance.history.split', 'migration_id')
    backup_ids = fields.One2many('erpmanager.backup', 'migration_id')

    include_saleorder = fields.Boolean(string='Migrate Sale Orders', help='Set true to migrate sale order')
    pricelist_vnd_id = fields.Many2one('product.pricelist', string='VND Pricelist', help='Default pricelist for VND sale order')
    pricelist_usd_id = fields.Many2one('product.pricelist', string='USD Pricelist', help='Default pricelist for USD sale order')
    plan_map_ids = fields.One2many('joomla.migration.erpmanger.plan.map', 'migration_id')
    saleorder_map_ids = fields.One2many('joomla.migration.erpmanager.saleorder.map', 'migration_id')

    def _get_joomla_models(self):
        jmodels = super(JoomlaMigration, self)._get_joomla_models()
        if self.include_erpmanager:
            for mod in self.pool.models:
                if mod.startswith('erpmanager'):
                    jmodels[mod] = 600
        return jmodels

    def _load_data(self):
        res = super(JoomlaMigration, self)._load_data()
        if self.include_erpmanager:
            if self.include_user:
                self._update_user_map()
            self._init_plan_map()
            self._init_saleorder_map()
        return res

    def _update_user_map(self):
        customer_users = self.saleorder_ids.mapped('customer_id.partner_id.uid')
        mapped_lines = self.user_map_ids.filtered(lambda r: r.joomla_user_id in customer_users)
        mapped_lines.write({'is_customer': True})
        not_mapped_users = customer_users - mapped_lines.mapped('joomla_user_id')
        for user in not_mapped_users:
            self.user_map_ids.create(dict(
                migration_id=self.id,
                joomla_user_id=user.id,
                is_customer=True
            ))

    def _get_user_map(self):
        Partner = self.env['res.partner']
        res = super(JoomlaMigration, self)._get_user_map()
        mapped_partners = Partner.browse([p.id for p in res.values()])
        not_mapped_jpartners = self.partner_ids.filtered(lambda p: p.uid not in res)

        jpartners_with_company_names = not_mapped_jpartners.filtered(lambda p: p.company_name)
        name_to_partner = {p.name.strip().lower(): p for p in Partner.search([]) - mapped_partners}
        for jpartner in jpartners_with_company_names:
            partner = name_to_partner.get(jpartner.company_name.strip().lower())
            if partner:
                res[jpartner.uid] = partner
                mapped_partners += partner
        return res

    def action_view_user_map(self):
        res = super(JoomlaMigration, self).action_view_user_map()
        if self.include_erpmanager:
            context = dict(res.get('context', {}))
            context['search_default_is_customer'] = 1
            res['context'] = context
        return res

    def action_view_saleorder_map(self):
        return dict(
            name='Sale Order Map',
            type='ir.actions.act_window',
            res_model='joomla.migration.erpmanager.saleorder.map',
            view_mode='tree',
            targe='new',
            domain='[("migration_id", "=", {})]'.format(self.id)
        )

    def _init_plan_map(self):
        for plan in self.plan_ids.filtered(lambda p: not p.istrial):
            self.plan_map_ids.create(dict(
                migration_id=self.id,
                joomla_plan_id=plan.id
            ))

    def _init_saleorder_map(self):
        for order in self.saleorder_ids:
            self.saleorder_map_ids.create(dict(
                migration_id=self.id,
                joomla_order_id=order.id
            ))

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_erpmanager:
            if self.include_saleorder and (not self.pricelist_usd_id or not self.pricelist_vnd_id):
                raise UserError('Please select default pricelist for sale order')
            self.with_context(tracking_disable=True)._migrate_erpmanager()

    def _migrate_erpmanager(self):
        self._disable_crons()
        self.wallet_ids.migrate()
        self.plan_ids.migrate()
        if self.include_saleorder:
            self.saleorder_ids.migrate()
        self.pserver_ids.migrate()
        self.ip_ids.migrate()
        self.proxyserver_ids.migrate()
        self.pgsqlserver_ids.migrate()
        self.dnsserver_ids.migrate()
        self.erpserver_ids.migrate()
        self.vserver_ids.migrate()
        self.basedomain_ids.migrate()
        self.instance_ids.migrate()
        self.instanceperm_ids.migrate()
        self.port_ids.migrate()
        self.subdomain_ids.migrate()
        self.blockedsubdomain_ids.migrate()
        self.customerdomain_ids.migrate()
        self.instance_ids.create_nginx_sites()
        self.defaulterpconfig_ids.migrate()
        self.erpconfig_ids.migrate()
        self.customerplan_ids.migrate()
        self.instance_history_ids.migrate()
        self.instance_history_split_ids.migrate()
        self.backup_ids.migrate()

    def _disable_crons(self):
        crons = self.env['ir.cron'].search([('name', 'ilike', 'odoo saas')])
        crons.write(dict(active=False))


class UserMap(models.TransientModel):
    _inherit = 'joomla.migration.user.map'

    is_customer = fields.Boolean(help='True if the user is associated with sale order')


class PlanMap(models.TransientModel):
    _name = 'joomla.migration.erpmanger.plan.map'
    _description = 'ERPManager Plan Map'

    migration_id = fields.Many2one('joomla.migration', required=True)
    joomla_plan_id = fields.Many2one('erpmanager.plan', required=True, ondelete='cascade')
    odoo_product_id = fields.Many2one('product.product')


class SaleOrderMap(models.TransientModel):
    _name = 'joomla.migration.erpmanager.saleorder.map'
    _description = 'ERPManager Sale Order Map'

    migration_id = fields.Many2one('joomla.migration', required=True)
    joomla_order_id = fields.Many2one('erpmanager.saleorder', required=True, ondelete='cascade')
    odoo_order_id = fields.Many2one('sale.order')
