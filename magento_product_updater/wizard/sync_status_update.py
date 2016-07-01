# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class UpdateSyncStatus(models.TransientModel):
    _name = "magento.update.sync.status"

    update_qty = fields.Selection([('Yes', _('Yes')), ('No', _('No'))], _('Update Quantity'), default='Yes')
    update_price = fields.Selection([('Yes', _('Yes')), ('No', _('No'))], _('Update Price'), default='Yes')

    @api.multi
    def update_sync_status(self):
        self.ensure_one()
        products = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_ids', []))
        products.write({'need_qty_sync': self.update_qty == 'Yes', 'need_price_sync': self.update_price == 'Yes'})
        return True
