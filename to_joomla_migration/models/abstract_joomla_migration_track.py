from odoo.osv import expression

from odoo import fields, models


class AbstractJoomlaMigrationTrack(models.AbstractModel):
    _inherit = 'abstract.joomla.migration.track'

    # Odoo does not allow relation with a transient model, so we use an Integer field here alternatively
    migration_id = fields.Integer(string='Migration ID',
                                  help="Technical field to map the record with Migration record temporarily")

    def get_migrated_data(self, website=None, jtable=None):
        website = website or self.env['joomla.migration'].get_current_migration().website_url
        if website:
            domain = [('old_website', '=', website)]
        else:
            domain = [('old_website', '!=', False)]
        if jtable:
            domain = expression.AND([domain, [('old_website_model', '=', jtable)]])
        return self.with_context(active_test=False).search(domain)

    def get_migrated_data_map(self, website=None, jtable=None):
        data = self.get_migrated_data(website, jtable)
        return {r.old_website_record_id: r for r in data}
