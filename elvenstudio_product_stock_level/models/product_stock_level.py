# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging
_log = logging.getLogger(__name__)

class ProductStockLevel(models.Model):
    _name = 'product.stocklevel'

    product_id = fields.Many2one(comodel_name='product.product')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse')

    qty_available = fields.Float()
    incoming_qty = fields.Float()
    outgoing_qty = fields.Float()
    virtual_available = fields.Float()
    immediately_usable_qty = fields.Float()

    sold = fields.Float()
    purchased = fields.Float()
    valuation = fields.Float()

    def _init_products(self, cr, uid, context=None):
        warehouses = self.pool.get('stock.warehouse').search(cr, uid, [])

        stocklevel = self.pool.get('product.stocklevel')

        i = 0
        prod_obj = self.pool.get('product.product')
        products = prod_obj.search(cr, uid, [('type', '!=', 'service')])
        for p in products:

            # if i > 100:
            #     break

            for warehouse in warehouses:
                stocklevel.update_stocklevel(cr, uid, warehouse, p)

            i += 1
            if i % 100 == 0:
                _log.info(str(i) + " product stocklevel updated")

        return True

    @api.model
    def update_stocklevel(self, warehouse_id, product_id):
        # compute stock level
        stocklevel = self.get_stock_level_by_warehouse(warehouse_id, product_id)

        if stocklevel:
            # stocklevel exists for given warehouse
            # update or create a stocklevel record
            record = self.search([('warehouse_id', '=', warehouse_id), ('product_id', '=', product_id)])

            # NB: assume in record there is only one stocklevel record
            if len(record) > 1:
                record.unlink()
                record = False

            if record:
                record.write({

                    'qty_available': stocklevel['qty_available'],
                    'incoming_qty': stocklevel['incoming_qty'],
                    'outgoing_qty': stocklevel['outgoing_qty'],
                    'virtual_available': stocklevel['virtual_available'],
                    'immediately_usable_qty': stocklevel['qty_available'] - stocklevel['outgoing_qty'],
                    'valuation': stocklevel['valuation'],
                    'sold': stocklevel['sold'],
                    'purchased': stocklevel['qty_available']
                })
            else:
                self.create({
                    'product_id': product_id,
                    'warehouse_id': warehouse_id,
                    'qty_available': stocklevel['qty_available'],
                    'incoming_qty': stocklevel['incoming_qty'],
                    'outgoing_qty': stocklevel['outgoing_qty'],
                    'virtual_available': stocklevel['virtual_available'],
                    'immediately_usable_qty': stocklevel['qty_available'] - stocklevel['outgoing_qty'],
                    'valuation': stocklevel['valuation'],
                    'sold': stocklevel['sold'],
                    'purchased': stocklevel['qty_available']
                })
        else:
            # no stocklevel for given warehouse
            # delete stocklevel records if any
            records = self.search([('warehouse_id', '=', warehouse_id), ('product_id', '=', product_id)])
            records.unlink()


    @api.model
    def get_stock_level_by_warehouse(self, warehouse_id, product_id):
        warehouse = self.env['stock.warehouse'].search([('id', '=', warehouse_id)])
        stock_locations = self.env['stock.location'].search([('location_id', 'child_of', warehouse.view_location_id.id)])
        customer_location_ids = self.env['stock.location'].search([('usage', '=', 'customer')])
        supplier_location_ids = self.env['stock.location'].search([('usage', '=', 'supplier')])

        customer_location_ids = '(' + str(customer_location_ids.ids or [0]).strip('[]') + ')'
        supplier_location_ids = '(' + str(supplier_location_ids.ids or [0]).strip('[]') + ')'

        location_ids = stock_locations.ids

        date_filter = ''
        # if dates:
        #     if dates.get('from_date') :
        #         date_filter = date_filter + 'and date::date >= ' + "'" + dates['from_date']+ "'"
        #     if dates.get('to_date') :
        #         date_filter = date_filter + 'and date::date <=' + "'" + dates['to_date']+ "'"

        # if not product_ids :
        #     return []
        # product_ids = '(' + str(product_ids).strip('[]') + ')'

        location_ids = '(' + str(location_ids or [0]).strip('[]') + ')'
        product_ids = '(' + str(product_id) + ')'

        qry="""
            select product,
                COALESCE(sum(report.qty_available),0) as qty_available,
                COALESCE(sum(report.valuation),0) as valuation,
                COALESCE(sum(report.qty_available),0)+COALESCE(sum(report.incoming),0)-COALESCE(sum(report.outgoing),0) as virtual_available,
                sum(incoming) as incoming_qty,
                sum(outgoing) as outgoing_qty,
                sum(sold) as sold,
                sum(purchased) as purchased  from
                (
                    select product,sum(qty) as qty_available ,sum(valuation) as valuation,0 as incoming, 0 as outgoing,0 as sold, 0 as purchased from
                        (
                            select quant.product_id as product,quant.qty as qty,(quant.qty * quant.cost) as valuation from stock_quant_move_rel,stock_quant as quant
                            where
                            stock_quant_move_rel.quant_id = quant.id AND stock_quant_move_rel.move_id in
                            (
                                select id from stock_move
                                where product_id in %s and location_dest_id in %s and state ='done' %s
                            )

                            union all
                            select quant.product_id as product,-quant.qty as qty,-(quant.qty * quant.cost) as valuation  from stock_quant_move_rel,stock_quant as quant
                            where
                            stock_quant_move_rel.quant_id = quant.id AND stock_quant_move_rel.move_id in
                            (
                                select id from stock_move
                                where product_id in %s and location_id in %s and state ='done' %s
                            )
                        ) as product_stock_available
                    group by product

                    union all
                    Select prod as product,0 as qty_available,0 as valuation, sum(stock_in_out_data.in) as incoming, sum(stock_in_out_data.out) as outgoing,0 as sold, 0 as purchased from
                        (
                            Select product_id as prod, sum(product_qty) as in, 0 as out from stock_move
                            where
                            product_id in %s
                            and location_id not in %s and location_dest_id in %s
                            and state in ('confirmed', 'waiting', 'assigned') %s
                            group by product_id

                            UNION
                            Select product_id as prod, 0 as in, sum(product_qty) as out from stock_move
                            where
                            product_id in %s
                            and location_id in %s and location_dest_id not in %s
                            and state in ('confirmed', 'waiting', 'assigned') %s
                            group by product_id

                        ) as stock_in_out_data
                    group by prod


            union all
            select stock_data.prod as product,0 as qty_available,0 as valuation,0 as incoming,0 as outgoing, sum(stock_data.sold) as sold, sum(stock_data.purchased) as purchased
                    from (
                            Select product_id as prod, sum(product_qty) as sold, 0 as purchased from stock_move
                                where
                                product_id in %s
                                and location_id in %s and location_dest_id in %s
                                and state='done' %s
                                group by product_id
                            UNION
                            Select product_id as prod, 0 as sold, sum(product_qty) as purchased from stock_move
                                where
                                product_id in %s
                                and location_id in %s and location_dest_id in %s
                                and state='done' %s
                                group by product_id
                            ) as stock_data group by prod

            ) report
            JOIN product_product P on (P.id = report.product)
            group by product order by product
        """%( product_ids,location_ids, date_filter,
              product_ids,location_ids, date_filter,
              product_ids,location_ids,location_ids, date_filter,
              product_ids,location_ids,location_ids, date_filter,
              product_ids,location_ids,customer_location_ids,date_filter,
              product_ids,supplier_location_ids,location_ids,date_filter
              )

        # _log.info(qry)

        self._cr.execute(qry)
        return self._cr.dictfetchone()
