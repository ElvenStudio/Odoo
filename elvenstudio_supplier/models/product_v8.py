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
        # _logger.warning('UPDATE PRODUCT ROUTE')
        # Carico l'ultima configurazione valida
        settings_obj = self.env['stock.config.settings'].search([('mto_route', '!=', 0)], limit=1, order="id DESC")

        if settings_obj and settings_obj.mto_route.id:
            # Memorizzo la rotta per evitare il refresh continuo della configurazione
            _route_id = settings_obj.mto_route.id

            # Creo le liste dei prodotti su cui aggiungere o rimuovere la rotta
            product_to_remove_mto = []
            product_to_add_mto = []

            for product in self:
                # Se la rotta c'è ma il prodotto non ha fornitori
                if _route_id in product.route_ids.ids and not product.supplier_ids.ids:
                    # rimuovo l'mto
                    product_to_remove_mto.append(product.id)
                # Se la rotta non c'è ma il prodotto ha fornitori
                elif _route_id not in product.route_ids.ids and product.supplier_ids.ids:
                    # aggiungo l'mto
                    product_to_add_mto.append(product.id)

                # Se la rotta non c'è e non ci sono fornitori non faccio nulla
                # Se la rotta c'è e ci sono fornitori non faccio nulla

            # Aggiorno le rotte alle liste di prodotti in blocco
            if product_to_add_mto:
                self.browse(product_to_add_mto).write({'route_ids': [(4, _route_id)], 'update_mto_route': False})

            if product_to_remove_mto:
                self.browse(product_to_remove_mto).write({'route_ids': [(3, _route_id)], 'update_mto_route': False})

    @api.multi
    def sort_suppliers(self):
        # _logger.warning('SORT SUPPLIER')
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
        # _logger.warning('WRITE PRODUCT')

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
