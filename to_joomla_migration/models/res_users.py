import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import now

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = 'res.users'

    created_from_existing_partner = fields.Boolean()

    def get_new_migrated_website(self):
        if self.partner_id.migration_id:
            jmigration_id = self.env['wizard.joomla.migration'].browse(self.partner_id.migration_id)
            if jmigration_id:
                return 'http://%s' % jmigration_id.to_website_id.domain
        return ''

    @api.multi
    def action_reset_password(self):
        """
        overriding the Odoo's action_reset_password
        create signup token for each user, and send their signup url by email
        """
        migrate_from_joomla = self._context.get('migrate_from_joomla', False)

        # if not joomla migration, fallback to the Odoo's default behaviour
        if not migrate_from_joomla:
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

