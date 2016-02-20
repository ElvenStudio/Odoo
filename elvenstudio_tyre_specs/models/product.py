# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api
from openerp.addons.elvenstudio_tyre.models.attribute_code import AttributeCode as AttrCode

_log = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.template"

    season = fields.Char(string='Stagione', index=True, size=20)
    tube = fields.Char(string='Camera', index=True, size=5)
    asse = fields.Char(string='Asse', index=True, size=20)
    etichetta_europea = fields.Char(string='Etichetta Europea', index=True)

    mud_snow = fields.Boolean(string='M+S', index=True)
    runflat = fields.Boolean(string='RFT', index=True)
    reinforced = fields.Boolean(string='XL', index=True)
    asse_sterzante = fields.Boolean(string='Sterzante', index=True)
    asse_trattivo = fields.Boolean(string='Trattivo', index=True)
    asse_rimorchio = fields.Boolean(string='Rimorchio', index=True)

    def _init_specs(self, cr, uid, context=None):
        _log.warning("Data Initialization")
        i = 0
        prod_obj = self.pool.get('product.template')
        products = prod_obj.search(cr, uid, [])
        for p in products:
            p = prod_obj.browse(cr, uid, p)
            data_to_save = p._get_specs_to_save_from_magento()
            if data_to_save:
                p.write(data_to_save)

            i += 1
            if i % 100 == 0:
                _log.warning(str(i) + " product updated")

        return True

    @api.model
    def get_attribute_to_save_from_magento(self):
        attributes = super(Product, self).get_attribute_to_save_from_magento()
        attributes.update(self._get_specs_to_save_from_magento())
        return attributes

    @api.model
    def _get_specs_to_save_from_magento(self):
        attributes = dict()
        magento_attrib = self._get_magento_attributes(self._get_specs_attribute_codes())

        season = self._get_dict_value(magento_attrib, AttrCode.Stagione)
        tube = self._get_dict_value(magento_attrib, AttrCode.Tube)
        asse = self._get_dict_value(magento_attrib, AttrCode.Asse)
        mud_snow = self._get_dict_value(magento_attrib, AttrCode.MudSnow) == 'SI'
        runflat = self._get_dict_value(magento_attrib, AttrCode.Runflat) == 'SI'
        reinforced = self._get_dict_value(magento_attrib, AttrCode.Reinforced) == 'SI'
        asse_sterzante = self._get_dict_value(magento_attrib, AttrCode.Asse_Sterzante) == 'SI'
        asse_trattivo = self._get_dict_value(magento_attrib, AttrCode.Asse_Trattivo) == 'SI'
        asse_rimorchio = self._get_dict_value(magento_attrib, AttrCode.Asse_Rimorchio) == 'SI'

        resistenza = self._get_dict_value(magento_attrib, AttrCode.Resistenza)
        aderenza = self._get_dict_value(magento_attrib, AttrCode.Aderenza)
        rumore = self._get_dict_value(magento_attrib, AttrCode.Rumore)
        bande = self._get_dict_value(magento_attrib, AttrCode.Bande)

        etichetta_europea = self._get_etichetta_europea(resistenza, aderenza, rumore, bande)

        attributes['season'] = season
        attributes['tube'] = tube
        attributes['asse'] = asse
        attributes['mud_snow'] = mud_snow
        attributes['runflat'] = runflat
        attributes['reinforced'] = reinforced
        attributes['asse_sterzante'] = asse_sterzante
        attributes['asse_trattivo'] = asse_trattivo
        attributes['asse_rimorchio'] = asse_rimorchio
        attributes['etichetta_europea'] = etichetta_europea

        return attributes

    @staticmethod
    def _get_tube_value(tube):
        return 'Tube Type' if tube == 'TT' else ('Tube Less' if tube == 'TL' else '')

    @staticmethod
    def _get_etichetta_europea(resistenza, aderenza, rumore, bande):
        try:
            rumore += 'dB' if isinstance(int(rumore), float) else ''
        except ValueError:
            pass

        return resistenza + \
            ((' ' + aderenza) if aderenza != '' else '') + \
            ((' ' + rumore) if aderenza + rumore != '' else '') + \
            ((' (' + bande + ' bande)') if aderenza + rumore + bande != '' else '')

    @staticmethod
    def _get_specs_attribute_codes():
        return {
            AttrCode.Stagione: AttrCode.Stagione,
            AttrCode.Tube: AttrCode.Tube,
            AttrCode.Asse: AttrCode.Asse,
            AttrCode.MudSnow: AttrCode.MudSnow,
            AttrCode.Runflat: AttrCode.Runflat,
            AttrCode.Reinforced: AttrCode.Reinforced,
            AttrCode.Asse_Sterzante: AttrCode.Asse_Sterzante,
            AttrCode.Asse_Trattivo: AttrCode.Asse_Trattivo,
            AttrCode.Asse_Rimorchio: AttrCode.Asse_Rimorchio,

            AttrCode.Resistenza: AttrCode.Resistenza,
            AttrCode.Aderenza: AttrCode.Aderenza,
            AttrCode.Rumore: AttrCode.Rumore,
            AttrCode.Bande: AttrCode.Bande,
        }
