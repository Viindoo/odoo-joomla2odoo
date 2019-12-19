from odoo import models, fields


class JoomlaMigration(models.TransientModel):
    _inherit = 'joomla.migration'

    include_erpmanager = fields.Boolean()
    db_table_prefix = fields.Char(default='lgzds_')
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

    def _get_joomla_models(self):
        jmodels = super(JoomlaMigration, self)._get_joomla_models()
        if self.include_erpmanager:
            for mod in self.pool.models:
                if mod.startswith('erpmanager'):
                    jmodels[mod] = 600
        return jmodels

    def _migrate_data(self):
        super(JoomlaMigration, self)._migrate_data()
        if self.include_erpmanager:
            self._migrate_erpmanager()

    def _migrate_erpmanager(self):
        self._disable_crons()
        self.wallet_ids.migrate()
        self.plan_ids.migrate()
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