# -*- coding: utf-8 -*-

from openerp import models, api
import logging

_log = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _check_product_routes(self):

        # Load all auto activable routes
        activable_routes = self.env['stock.location.route'].sudo().search(
            [
                ('product_selectable', '=', True),
                ('auto_activate_route', '=', True)
            ]
        )

        # Get all warehouses related to the activable routes
        warehouses = activable_routes.mapped('warehouse_ids')

        warehouse_routes = dict()
        # warehouse_routes = { w_id: stock.location.route(,,,) }

        # For each warehouse, associate their respective auto activable routes
        for warehouse_id in warehouses.ids:
            warehouse_routes[warehouse_id] = activable_routes.filtered(lambda r: warehouse_id in r.warehouse_ids.ids)

        # Get all product from the selected quants
        products = self.mapped('product_id')

        # Get all quant related to products
        quants = self.search([('product_id', 'in', products.ids), ('location_id.usage', '=', 'internal')])

        location_obj = self.env['stock.location']
        # Get the quants related to the warehouse with auto activable routes
        quants_to_check = quants.filtered(lambda q: location_obj.get_warehouse(q.location_id) in warehouses.ids)

        warehouse_products = dict()
        # warehouse_products = { w_id:
        #                          { p_id:
        #                              { 'qty': qty }
        #                          }
        #                      }

        # For each quant, get the product and associate him to the related warehouse
        #  grouping them by product id and sum the quantity
        for quant in quants_to_check:
            product_id = quant.product_id.id
            warehouse_id = location_obj.get_warehouse(quant.location_id)

            if warehouse_id not in warehouse_products:
                warehouse_products[warehouse_id] = {product_id: {'qty': quant.qty}}
            else:
                if product_id not in warehouse_products[warehouse_id]:
                    warehouse_products[warehouse_id][product_id] = {'qty': quant.qty}
                else:
                    old_qty = warehouse_products[warehouse_id][product_id]['qty']
                    warehouse_products[warehouse_id][product_id]['qty'] = old_qty + quant.qty

        product_updated = set()

        # For each warehouse,
        #  enable the routes for product with qty > 0 and
        #  disable the routes for product with qty <= 0
        for warehouse_id in warehouse_products:
            product_to_enable_route = set()
            product_to_disable_route = set()

            for product_id in warehouse_products[warehouse_id]:
                if warehouse_products[warehouse_id][product_id]['qty'] > 0:
                    product_to_enable_route.add(product_id)
                else:
                    product_to_disable_route.add(product_id)

            # Save for each warehouse the products that will be updated
            product_updated = product_updated.union(product_to_enable_route).union(product_to_disable_route)

            for route in warehouse_routes[warehouse_id]:
                self.env['product.product'].search([('id', 'in', list(product_to_disable_route))]).write(
                    {'route_ids': [(3, route.id)]})

                self.env['product.product'].search([('id', 'in', list(product_to_enable_route))]).write(
                    {'route_ids': [(4, route.id)]})

        # Get the products not updated, because we need to check and reset them
        product_to_update = set(products.ids) - product_updated

        for route in activable_routes:
            self.env['product.product'].search([('id', 'in', list(product_to_update))]).write(
                {'route_ids': [(3, route.id)]})

    @api.multi
    def write(self, values):
        # At each quant update will be raised a write
        result = super(StockQuant, self).write(values)
        self._check_product_routes()
        return result

    @api.model
    def _quant_create(self, qty, move,
                      lot_id=False,
                      owner_id=False,
                      src_package_id=False,
                      dest_package_id=False,
                      force_location_from=False,
                      force_location_to=False):

        # At each quant creation will be raised _quant_create and not the default create
        result = super(StockQuant, self)._quant_create(qty, move,
                                                       lot_id=lot_id,
                                                       owner_id=owner_id,
                                                       src_package_id=src_package_id,
                                                       dest_package_id=dest_package_id,
                                                       force_location_from=force_location_from,
                                                       force_location_to=force_location_to)

        result._check_product_routes()
        return result
