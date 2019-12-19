from odoo import models, fields


class ERPManagerCustomerDomain(models.TransientModel):
    _name = 'erpmanager.customerdomain'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Customer Domain'
    _joomla_table = 'erpmanager_customerdomain'

    name = fields.Char(joomla_column=True)
    ssl_certificate = fields.Text(joomla_column=True)
    ssl_certificate_key = fields.Text(joomla_column=True)
    instance_id = fields.Many2one('erpmanager.instance', joomla_column=True)
    customer_id = fields.Many2one('erpmanager.customer', joomla_column=True)
    odoo_id = fields.Many2one('custom.domain.name')

    def _prepare_custom_domain_values(self):
        self.ensure_one()
        values = dict(
            fqdn=self.name,
            partner_id=self.customer_id.odoo_id.id,
            instance_id=self.instance_id.odoo_id.id
        )
        if self.ssl_certificate:
            cert_values = self._prepare_ssl_certificate_values(self.name, self.ssl_certificate, self.ssl_certificate_key)
            cert = self.env['ssl.certificate'].create(cert_values)
            values.update(ssl_certificate_id=cert.id)
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_custom_domain_values()
        domain = self.env['custom.domain.name'].create(values)
        return domain

    def migrate(self):
        super(ERPManagerCustomerDomain, self.filtered(lambda domain: domain.instance_id)).migrate()
