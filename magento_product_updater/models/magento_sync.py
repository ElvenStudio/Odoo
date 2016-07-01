# -*- coding: utf-8 -*-

from openerp import models, api
from magento_xmlrpc_client import MagentoXmlRpcClient


class MagentoSynchronization(models.Model):
    _inherit = "magento.synchronization"

    @api.model
    def sync_to_magento(self, data):
        magento_conf = self.env['magento.configure'].get_active_configuration()
        magento = MagentoXmlRpcClient(magento_conf.name, magento_conf.user, magento_conf.pwd)
        magento.connect()
        result = magento.multi_call(data)
        magento.disconnect()
        self._write_sync_result(result)
        return result

    @api.model
    def cron_sync_product(self, sync_need_only=True, sync_qty=True, sync_price=True, use_product_template=False):
        search_domain = []

        if sync_need_only:
            # get only products that need to be synced

            if sync_price:
                search_domain.append(('need_price_sync', '=', True))

            if sync_qty:
                search_domain.append(('need_qty_sync', '=', True))

            if search_domain:
                # some search domain are added, so we need to add the conjunction
                search_domain.insert(0, '|')

        if use_product_template:
            # use product.template to find products to update
            products = self.env['magento.product.template'].search(search_domain)
        else:
            products = self.env['magento.product'].search(search_domain)

        products.sync_inventory_to_magento(sync_qty=sync_qty, sync_price=sync_price)

    @api.model
    def clean_sync_result(self):
        self.env['magento.sync.history'].search([]).unlink()
        return True

    @api.model
    def _write_sync_result(self, result=[]):

        # result is a list of list
        # each sublist is a chunk of multicall
        # Example result = [[True, True, True], [True, {'error':'error_msg'}, True]]
        flat_result = [item for sub_list in result for item in sub_list]

        status = 'yes' if reduce(lambda x, y: x is True and y is True, flat_result) else 'no'

        error_message = reduce(
            lambda x, y: (str(x) + "\n" if x is not True else '') + (str(y) + "\n" if y is not True else ''),
            flat_result
        )

        self.env['magento.sync.history'].create(
            {
                'status': status,
                'action_on': 'product',
                'action': 'c',
                'error_message': error_message
            }
        )
