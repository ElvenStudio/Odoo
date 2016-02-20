# -*- coding: utf-8 -*-

from openerp import models, fields


class MagentoAttribute(models.Model):
    """
    Estendo magento.attributes per aggiungere l'indice sul campo name,
    perchè usato frequentemente nelle ricerche.
    """
    _inherit = "magento.attributes"

    name = fields.Char('Attribute code', size=100, index=True)


class ProductAttributes(models.Model):
    """
    Estendo product.attributes per aggiungere l'etichetta e la chiave di un attributo magento,
    in quanto il modulo di base le ha referenziate in una model più interna.
    """
    _inherit = "product.attributes"

    label = fields.Char(related='attribute_id.label', readonly=True, copy=False)
    code = fields.Char(related='attribute_id.name', readonly=True, copy=False)
