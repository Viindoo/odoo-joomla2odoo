import base64
import json

from odoo import models


class AbstractERPManagerModel(models.AbstractModel):
    _name = 'abstract.erpmanager.model'
    _inherit = 'abstract.joomla.model'
    _description = 'Abstract ERPManager Model'

    def _prepare_ssl_certificate_values(self, domain_name, cert_txt, key_txt):
        cert = base64.b64encode(cert_txt.encode())
        key = base64.b64encode(key_txt.encode())
        values = dict(
            certificate_bin=cert,
            certificate_key_bin=key,
            cert_filename=domain_name + '.fullchain.pem',
            cert_key_filename=domain_name + '.privkey.pem'
        )
        return values

    def _deserialize_config_value(self, value):
        if value:
            if value.startswith('{'):
                return ','.join(json.loads(value).values())
        return value
