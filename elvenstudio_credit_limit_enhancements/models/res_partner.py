# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

# import logging
# _log = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):

        if 'credit_limit' in vals:
            partners = self.filtered(lambda p: not p.parent_id)

            for partner in partners:
                old = str(partner.credit_limit)
                new = str(vals['credit_limit'])
                partner.message_post(body=_("Credit limit modified: %s &rArr; %s") % (old, new))

        return super(ResPartner, self).write(vals)