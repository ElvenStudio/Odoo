# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class ProductV8(models.Model):
    _inherit = "product.template"

    supplier_qty = fields.Float(
        compute='_get_supplier_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        store=True
    )

    supplier_price = fields.Float(
        compute='_get_supplier_price',
        store=True
    )

    @api.one
    @api.depends('supplier_ids.available_qty')
    def _get_supplier_qty(self):
        self.supplier_qty = self.supplier_ids.get_supplier_qty()

    @api.one
    @api.depends('supplier_ids.pricelist_ids.price')
    def _get_supplier_price(self):
        self.supplier_price = self.supplier_ids.get_supplier_price()

    @api.multi
    def update_mto_route(self):

        # Carico le rotte attive
        active_routes = self.env['supplier.stock.location.routes'].sudo().search([('active', '=', True)])
        if active_routes:
            # Creo le liste dei prodotti su cui aggiungere o rimuovere la rotta
            product_to_remove_mto = {}
            product_to_add_mto = {}

            active_route_ids = set(map(lambda r: r.route.id, active_routes))
            for product in self:
                product_route_ids = set(product.route_ids.ids)

                # Se il prodotto non ha fornitori
                if not product.supplier_ids.ids:
                    # Se il prodotto ha delle rotte tra quelle attive, allora vanno rimosse
                    routes_to_remove = list(set.intersection(active_route_ids, product_route_ids))
                    product_to_remove_mto.update(
                        dict(
                            zip(
                                routes_to_remove,
                                map(
                                    lambda r: product_to_remove_mto.get(r, set()) | set([product.id]),
                                    routes_to_remove
                                )
                            )
                        )
                    )
                    # Altrimenti Se il prodotto non ha fornitori e non ha rotte attive non faccio nulla

                # Altrimenti se il prodotto ha fornitori
                else:
                    # Se il prodotto non ha delle rotte tra quelle attive, allora vanno aggiunte
                    routes_to_add = list(active_route_ids - product_route_ids)
                    product_to_add_mto.update(
                        dict(
                            zip(
                                routes_to_add,
                                map(
                                    lambda r: product_to_add_mto.get(r, set()) | set([product.id]),
                                    routes_to_add
                                )
                            )
                        )
                    )
                    # Altrimenti Se il prodotto ha fornitori e tutte le rotte sono già attive non faccio nulla

            # Aggiorno le rotte alle liste di prodotti in blocco
            for route_id, product_ids in product_to_add_mto.items():
                if product_ids:
                    self.browse(product_ids).write({'route_ids': [(4, route_id)], 'update_mto_route': False})

            for route_id, product_ids in product_to_remove_mto.items():
                if product_ids:
                    self.browse(product_ids).write({'route_ids': [(3, route_id)], 'update_mto_route': False})

    @api.multi
    def sort_suppliers(self):
        price_list_info_obj = self.env['pricelist.partnerinfo']
        sup_info_obj = self.env['product.supplierinfo']

        for product in self:
            supplier_ids = product.supplier_ids.ids

            if supplier_ids and len(supplier_ids) > 1:
                price_list = price_list_info_obj.search(
                    [
                        ('suppinfo_id', 'in', supplier_ids),
                        ('available_qty', '>', 0)
                    ],
                    order="price ASC"
                )

                i = 1
                ordered_supplier_ids = []
                for price_line in price_list:
                    if price_line.suppinfo_id.id not in ordered_supplier_ids:
                        ordered_supplier_ids.append(price_line.suppinfo_id.id)
                        sup_info_obj.browse([price_line.suppinfo_id.id]).write({'sequence': i, 'sort_suppliers': False})
                        i += 1
                    if price_line.suppinfo_id.id in supplier_ids:
                        supplier_ids.remove(price_line.suppinfo_id.id)

                for dangling_supplier in supplier_ids:
                    sup_info_obj.browse([dangling_supplier]).write({'sequence': i, 'sort_suppliers': False})
                    i += 1

    @api.multi
    def write(self, values):

        update_mto = True
        if 'update_mto_route' in values:
            update_mto = values['update_mto_route']
            values.pop('update_mto_route')

        result = super(ProductV8, self).write(values)

        # Se nel dizionario non è presente la chiave 'update_mto_route' allora
        # il salvataggio non proviene dal modulo, quindi avvio la procedura
        # di controllo delle rotte attive in base ai fornitori presenti
        if update_mto:
            self.update_mto_route()

        return result
