from odoo import models, fields


class ERPManagerWallet(models.TransientModel):
    _name = 'erpmanager.wallet'
    _inherit = 'abstract.erpmanager.model'
    _description = 'ERPManager Wallet'
    _joomla_table = 'erpmanager_wallet'

    currency_id = fields.Many2one('erpmanager.currency', joomla_column=True)
    amount = fields.Float(joomla_column=True)
    partner_id = fields.Many2one('erpmanager.partner', joomla_column=True)
    odoo_id = fields.Many2one('odoo.wallet')

    def _prepare_wallet_values(self):
        self.ensure_one()
        values = dict(
            currency_id=self.currency_id.odoo_id.id,
            amount=self.amount,
            partner_id=self.partner_id.odoo_id.id
        )
        values.update(self._prepare_track_values())
        return values

    def _migrate(self):
        self.ensure_one()
        values = self._prepare_wallet_values()
        wallet = self.env['odoo.wallet'].create(values)
        return wallet
