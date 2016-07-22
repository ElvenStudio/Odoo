# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api
from attribute_code import AttributeCode

_log = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.template"

    tipo_pneumatico = fields.Char(string='Tipo di Pneumatico')
    ip_code = fields.Char(string='Ip Code', index=True)
    magento_manufacturer = fields.Char(string='Marca', index=True)

    def _init_tyre(self, cr, uid, context=None):
        i = 0
        prod_obj = self.pool.get('product.template')
        products = prod_obj.search(cr, uid, [])
        for p in products:
            p = prod_obj.browse(cr, uid, p)
            p.write(p.get_attribute_to_save_from_magento())

            i += 1
            if i % 100 == 0:
                _log.info(str(i) + " product updated")

        return True

    @api.multi
    def reload_magento_attributes(self):
        for product in self:
            product.write(product.get_attribute_to_save_from_magento())

    @api.model
    def get_attribute_to_save_from_magento(self):
        attributes = dict()
        attributes.update(self._get_default_tyre_data_to_save_from_magento())
        return attributes

    @api.model
    def _get_default_tyre_data_to_save_from_magento(self):
        attributes = dict()
        magento_attrib = self._get_magento_attributes({
            AttributeCode.IpCode: AttributeCode.IpCode,
            AttributeCode.Marca: AttributeCode.Marca
        })

        attributes['tipo_pneumatico'] = self._get_attribute_set_name()
        attributes['ip_code'] = self._get_dict_value(magento_attrib, AttributeCode.IpCode)
        attributes['magento_manufacturer'] = self._get_dict_value(magento_attrib, AttributeCode.Marca)
        return attributes

    @api.model
    def _get_attribute_set_name(self):
        return self.attribute_set_id.name if self.attribute_set_id and self.attribute_set_id.name else 'none'

    @api.model
    def _get_magento_attributes(self, attr_codes=dict()):
        attributes = dict()

        if self.attribute_set_id and AttributeCode.Pneumatico in self.attribute_set_id.name:
            product_attributes = self.env['product.attributes'].search(
                [('fkey_product', '=', self.id), ('code', 'in', attr_codes.keys())]
            )

            attributes = {code: value for code, value in map(lambda attr: (attr.code, attr.value), product_attributes)}
            for key, new_key in attr_codes.iteritems():
                if key in attributes:
                    attributes[new_key] = attributes.pop(key)

        return attributes

    @api.model
    def _get_all_magento_attributes(self):
        attributes = dict()

        if self.attribute_set_id:
            if AttributeCode.Pneumatico in self.attribute_set_id.name:

                magento_attributes = self.env['product.attributes'].search(
                    [('fkey_product', '=', self.id)], order="id asc")

                for attribute in magento_attributes:
                    key = attribute.code

                    if AttributeCode.Larghezza in attribute.code:
                        key = AttributeCode.Larghezza

                    if AttributeCode.Sezione_Auto == attribute.code or \
                        AttributeCode.Sezione_Moto == attribute.code or \
                            AttributeCode.Sezione_Autocarro == attribute.code:
                        key = AttributeCode.Sezione

                    if AttributeCode.Cerchio in attribute.code:
                        key = AttributeCode.Cerchio

                    if AttributeCode.Asse in attribute.code:
                        key = AttributeCode.Asse

                    attributes[key] = attribute.value

        return attributes

    @staticmethod
    def _get_dict_value(dictionary, key, default=''):
        return dictionary[key] if key in dictionary else default
