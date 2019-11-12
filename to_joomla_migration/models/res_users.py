import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = 'res.users'

    created_from_existing_partner = fields.Boolean()

    def get_new_migrated_website(self):
        domain = self.migration_id.to_website_id.domain
        return 'http://{}'.format(domain) if domain else ''

    @api.multi
    def action_reset_password(self):
        """
        overriding the Odoo's action_reset_password
        create signup token for each user, and send their signup url by email
        """
        joomla_migration = self._context.get('joomla_migration', False)

        # if not joomla migration, fallback to the Odoo's default behaviour
        if not joomla_migration:
            super(User, self).action_reset_password()
        else:
            # no time limit for initial invitation
            self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=False)

            # send email to users with their signup url
            template = self.env.ref('to_joomla_migration.user_account_migration_notif', raise_if_not_found=True)

            template_values = {
                'email_to': '${object.email|safe}',
                'email_cc': False,
                'auto_delete': True,
                'partner_to': False,
                'scheduled_date': False,
            }
            template.write(template_values)

            for user in self:
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                with self.env.cr.savepoint():
                    template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    def get_migrated_data(self):
        return self.with_context(active_test=False).search([('migration_id', '!=', False)])