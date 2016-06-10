Sale Margin Enhancement
=======================

The module extends sale_margin adding this functionalities:
-----------------------------------------------------------
**Margin Computation Enhancements:**

 - saves the purchase price into sale order lines from product cost price or standard price;
 - computes margin using product uom quantity instead of product uos quantity;
 - adds a bulk action to recompute sale order margins;
 - adds cron to recompute margins.
 
**New Group for selling product below the purchase price:**

 - new _Sale margin options_ category that can be assigne to user;
 - each user can see the purchase price on sale order and sale invoice;
 - each user can be able to edit or not the unit price;
 - each user can sell or not below the purchase price.

Credits
=======

Contributors
------------
* Domenico Stragapede <d.stragapede@elvenstudio.it>
* Vincenzo Terzulli <v.terzulli@elvenstudio.it>