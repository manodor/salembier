from odoo import models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def _onchange_product_id_set_product_packaging(self):
        if self.product_id.packaging_ids:
            packaging_ids = self.product_id.packaging_ids
            packaging_ids = packaging_ids.filtered(lambda p: p.purchase)
            # .filtered(
            #     lambda p: (p.qty == 0.0) or (self.product_uom_qty <= p.qty > 0.0)
            # )
            packaing_id = packaging_ids[0] if packaging_ids else False
            if packaing_id:
                if packaing_id.qty:
                    self.product_qty = packaing_id.qty
                self.product_packaging_id = packaing_id

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return
        seller_min_qty = self.product_id.seller_ids\
            .filtered(lambda r: r.name == self.order_id.partner_id and (not r.product_id or r.product_id == self.product_id))\
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom = seller_min_qty[0].product_uom
        else:
            self.product_qty = 1.0
        if self.product_packaging_id:
            self.product_qty = self.product_packaging_id.qty

    @api.onchange('product_id', 'product_qty', 'product_uom')
    def _onchange_suggest_packaging(self):
        # remove packaging if not match the product
        if self.product_packaging_id.product_id != self.product_id:
            self.product_packaging_id = False
        # suggest biggest suitable packaging
        # if self.product_id and self.product_uom_qty and self.product_uom:
        #     self.product_packaging_id = self.product_id.packaging_ids.filtered(
        #         'sales')._find_suitable_product_packaging(self.product_uom_qty, self.product_uom)

    @api.constrains("product_id", "product_packaging_id", "product_packaging_qty")
    def _check_product_packaging_sell_only_by_packaging(self):
        for line in self:
            if not line.product_id.packaging_ids.filtered(lambda p: p.purchase):
                continue
            if line.product_packaging_id:
                newqty = line.product_packaging_id._check_qty(line.product_uom_qty, line.product_uom, "UP")
                if float_compare(newqty, line.product_uom_qty, precision_rounding=line.product_uom.rounding) != 0:
                    raise ValidationError(_("Product \" %s \" can only be sold with a packaging and a "
                                            "packaging qantity." % line.product_id.name))

    @api.onchange('product_packaging_id', 'product_qty')
    def _onchange_product_packaging_id(self):
        if self.product_packaging_id and self.product_qty:
            newqty = self.product_packaging_id._check_qty(self.product_qty, self.product_uom, "UP")
            if float_compare(newqty, self.product_uom_qty, precision_rounding=self.product_uom.rounding) != 0:
                return {
                    'warning': {
                        'title': _('Warning'),
                        'message': _(
                            "This product is packaged by %(pack_size).2f %(pack_name)s. You should sell %(quantity).2f %(unit)s.",
                            pack_size=self.product_packaging_id.qty,
                            pack_name=self.product_id.uom_id.name,
                            quantity=newqty,
                            unit=self.product_uom.name
                        ),
                    },
                }