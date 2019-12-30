import itertools
import os

from odoo import models, fields


class ERPManagerInstance(models.TransientModel):
    _name = 'erpmanager.instance'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Instance'
    _joomla_table = 'erpmanager_instance'

    vserver_id = fields.Many2one('erpmanager.vserver', joomla_column=True)
    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    max_bwpermonth = fields.Float(joomla_column=True)
    max_uaccounts = fields.Float(joomla_column=True)
    max_backup = fields.Integer(joomla_column=True)
    max_spacesize = fields.Float(joomla_column=True)
    allow_custommodule = fields.Boolean(joomla_column=True)
    istrial = fields.Boolean(joomla_column=True)
    technical_name = fields.Char(joomla_column=True)
    published = fields.Boolean(joomla_column=True)
    publish_up = fields.Datetime(joomla_column=True)
    publish_down = fields.Datetime(joomla_column=True)
    created = fields.Datetime(joomla_column=True)
    addons_path = fields.Char(compute='_compute_configs')
    db_password = fields.Char(compute='_compute_configs')
    admin_passwd = fields.Char(compute='_compute_configs')
    http_port = fields.Integer(compute='_compute_configs', string='HTTP Port Number')
    http_port_id = fields.Many2one('erpmanager.port', compute='_compute_ports')
    longpolling_port = fields.Integer(compute='_compute_configs', string='Longpolling Port Number')
    longpolling_port_id = fields.Many2one('erpmanager.port', compute='_compute_ports')
    subdomain_ids = fields.One2many('erpmanager.subdomain', 'instance_id')
    customerdomain_ids = fields.One2many('erpmanager.customerdomain', 'instance_id')
    instanceperm_ids = fields.One2many('erpmanager.instanceperm', 'instance_id')
    odoo_id = fields.Many2one('odoo.instance')

    def _compute_configs(self):
        keys = ['addons_path', 'db_password', 'admin_passwd', 'http_port', 'longpolling_port']
        configs = self.env['erpmanager.erpconfig'].search([('name', 'in', keys)])
        for instance in self:
            instance_configs = configs.filtered(lambda c: c.oebackend_id.instance_id == instance)
            for key in keys:
                instance[key] = instance_configs.filtered(lambda c: c.name == key)[:1].value

    def _compute_ports(self):
        ports = self.env['erpmanager.port'].search([('oebackend_id', '!=', False)])
        for instance in self:
            instance_ports = ports.filtered(lambda p: p.oebackend_id.instance_id == instance)
            instance.http_port_id = instance_ports.filtered(lambda p: p.name == instance.http_port)
            instance.longpolling_port_id = instance_ports.filtered(lambda p: p.name == instance.longpolling_port)

    def _get_custom_addons_path(self):
        self.ensure_one()
        addons_paths = self._deserialize_config_value(self.addons_path)
        std_addons_paths = self.vserver_id.erpserver_ids[:1]._get_addons_paths()
        std_addons_dir_names = set(os.path.basename(p) for p in std_addons_paths)
        custom_addons_paths = []
        for path in addons_paths.split(','):
            dir_name = os.path.basename(path)
            if dir_name not in std_addons_dir_names:
                custom_addons_paths.append(path)
        return custom_addons_paths

    def _prepare_custom_addons_path_values(self):
        self.ensure_one()
        paths = self._get_custom_addons_path()
        values = []
        for path in paths:
            server_path = self.env['server.dir.path'].create(dict(name=path))
            values.append((0, 0, dict(addons_path_id=server_path.id)))
        return values

    def _prepare_odoo_instance_values(self):
        self.ensure_one()
        custom_addons_path_values = self._prepare_custom_addons_path_values()
        domain = self.subdomain_ids[0]
        values = dict(
            name=domain.name,
            zone_id=domain.basedomain_id.odoo_id.id,
            service_name=self.technical_name,
            partner_id=self.customer_id.odoo_id.id,
            odoo_version_id=self.vserver_id.odoo_id.odoo_version_id.id,
            vserver_id=self.vserver_id.odoo_id.id,
            max_uaccounts=self.max_uaccounts,
            max_storage=self.max_spacesize,
            max_bandwidth=self.max_bwpermonth,
            max_backups=self.max_backup,
            allow_custom_modules=self.allow_custommodule,
            custom_addons_path_ids=custom_addons_path_values,
            state='deployed' if self.published else 'disabled',
            is_trial=self.istrial,
            trial_days=15 if self.istrial else 0,
            start_date=self.created,
            db_password=self.db_password,
            admin_password=self.admin_passwd,
            http_port_id=self.http_port_id.odoo_id.id,
            longpolling_port_id=self.longpolling_port_id.odoo_id.id,
            is_running=self.published
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_odoo_instance_values()
        instance = self.env['odoo.instance'].create(values)
        return instance

    def _prepare_nginx_site_values(self, fqdn, ssl_cert):
        self.ensure_one()
        values = dict(
            name=fqdn,
            ssl_certificate_id=ssl_cert.id,
            nginx_server_id=self.vserver_id.proxyserver_ids[:1].odoo_id.id,
            upstream_ip=self.vserver_id.erpserver_ids[:1].working_ip_id.name,
            upstream_port=self.http_port,
            upstream_longpolling_port=self.longpolling_port,
            instance_id=self.odoo_id.id
        )
        return values

    def _create_nginx_site(self):
        self.ensure_one()
        vals_list = []
        for domain in itertools.chain(self.subdomain_ids.mapped('odoo_id'),
                                      self.customerdomain_ids.mapped('odoo_id')):
            vals_list.append(self._prepare_nginx_site_values(domain.fqdn, domain.ssl_certificate_id))
        self.env['nginx.site'].create(vals_list)

    def create_nginx_sites(self):
        for idx, instance in enumerate(self, start=1):
            self._logger.info('[{}/{}] Creating nginx sites for instance {}'.format(idx, len(self), instance.odoo_id.fqdn))
            if not instance.odoo_id.nginx_site_ids:
                instance._create_nginx_site()
