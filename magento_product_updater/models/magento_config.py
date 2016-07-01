# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class MagentoConfigure(models.Model):
    _inherit = "magento.configure"

    pricelist_id = fields.Many2one(
        'product.pricelist',
        _('Product Pricelist'),
        help=_('The pricelist used to export the price.\n If not defined will be used the Public Price.')
    )

    @api.model
    def get_active_configuration(self):
        config_id = self.search([('active', '=', True)])

        if len(config_id) > 1:
            raise except_orm(_('Error'), _("Sorry, only one Active Configuration setting is allowed."))
        elif not config_id:
            raise except_orm(_('Error'), _("Please create the configuration part for Magento connection!!!"))
        else:
            return config_id

    @api.model
    def get_active_pricelist_id(self):
        return self.get_active_configuration().pricelist_id
