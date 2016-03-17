Supplier Pricelist Management
==============================================================

Improved Supplier pricelists manamegent
==============================================================

This module extends the supplier pricelists with this functionalities:
 - Adds, for each supplier of a product, the maximum buyable quantity
 - Shows, in product kanban view, the main supplier quantity and the main supplier price
 - Product supplier's with buyable quantity are sorted automatically, the other are put at last.
 - Adds a new menu for importing pricelists and logs OK/KO imported lines
 - Activate and deactivate pricelists automatically, based on start/end date.
 - Select which location routes will be added/removed to the product when a supplier will be added/removed.

Usage:
------
In __Elvenstudio -> Configuration -> Location Routes__ add how many location routes you need to activate
when a supplier will be added to a product.
In __Elvenstudio -> Product Suppliers -> Pricelists__ you can add new pricelists, using a well-formed CSV file
(provided in data/pricelist.csv).


TODO:
-----
  - Batch pricelist import
  - Reports and pivot table for price analisys