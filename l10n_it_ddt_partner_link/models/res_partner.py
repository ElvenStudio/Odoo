# -*- coding: utf-8 -*-

from openerp import models, fields, api
# import logging

# _logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    total_ddt = fields.Integer(compute='_count_partner_ddts')

    @api.one
    def _count_partner_ddts(self):
        ddt_obj = self.env['stock.picking.package.preparation']
        self.total_ddt = len(ddt_obj.search([('partner_invoice_id', '=', self[0].id)]))

    @api.multi
    def action_open_partner_ddt(self):

        # _logger.warning("AWE")
        """ Open ddt list view of the partner """
        action_ref = 'stock_picking_package_preparation.action_stock_picking_package_preparation'
        action_dict = self.env.ref(action_ref).read()[0]

        # _logger.warning("dictionary " + str(action_dict))
        # ddt_obj = self.env['stock.picking.package.preparation']
        # ddts = ddt_obj.search(['partner_invoice_id', '=', self[0].id])

        action_dict['domain'] = [('partner_invoice_id', '=', self[0].id)]

        # _logger.warning("dictionary with domain " + str(action_dict))

        return action_dict
