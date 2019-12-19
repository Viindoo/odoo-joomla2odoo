from odoo import models, fields


class ERPManagerInstancePerm(models.TransientModel):
    _name = 'erpmanager.instanceperm'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Instance Perm'
    _joomla_table = 'erpmanager_instanceperm'

    technical_name = fields.Char(joomla_column=True)
    fullsubdomain_name = fields.Char(joomla_column=True)
    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    odoo_id = fields.Many2one('odoo.instance.perm')

    processed_items = {}

    def _prepare_instance_perm_values(self):
        self.ensure_one()
        values = dict(
            instance_id=self.instance_id.odoo_id.id,
            service_name=self.technical_name,
            fqdn=self.fullsubdomain_name,
            partner_id=self.customer_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _get_matching_data(self, odoo_model):
        return self._get_matching_data_by_field(odoo_model, 'technical_name', 'service_name')

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_instance_perm_values()
        instanceperm = self.processed_items.get(self.technical_name)
        if not instanceperm:
            instanceperm = self.env['odoo.instance.perm'].create(values)
            self.processed_items[self.technical_name] = instanceperm
        return instanceperm

    def migrate(self):
        self.processed_items = {}
        super(ERPManagerInstancePerm, self).migrate()
