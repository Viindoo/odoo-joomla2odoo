from odoo import models


class WizardJoomlaMigration(models.TransientModel):
    _inherit = 'wizard.joomla.migration'

    def _prepare_doc_content_values(self, article):
        values = super(WizardJoomlaMigration, self)._prepare_doc_content_values(article)
        values.update(odoo_version_id=self.env.ref('to_odoo_version.odoo_v8').id)
        return values
