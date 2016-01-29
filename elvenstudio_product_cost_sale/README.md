Product Sale Cost
==============================================================

Add a product cost that depends on the current stock and the supplier price.
------------------------------------
This module adds a new product cost called cost_sale, that is evaluated as follow:
 * if the product is in stock, the cost is equal to the variant cost price;
 * if the product is not in stock, the price is got from the main supplier.
 * if the context need a quantity Q of the product and the shock has q1 < Q the cost is:
   cost_sale = (q1 * variant_cost_price + (Q - q1) * supplier price ) / Q.

This new cost_sale can be used in product pricelist as base cost for pricelists.