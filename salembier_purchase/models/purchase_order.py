from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_ref_supplier(self):
        if self.product_id:
            if len(self.product_id.variant_seller_ids) == 1:
                filter = self.product_id.variant_seller_ids.filtered(
                    lambda r: r.name == self.order_id.partner_id)
                self.product_supplier_ref = filter.product_code
                self.name = filter.product_name
            else:
                filter = self.product_id.seller_ids.filtered(
                    lambda r: r.name == self.order_id.partner_id and r.product_id == self.product_id)
                self.product_supplier_ref = filter.product_code
                self.name = filter.product_name

    product_supplier_ref = fields.Char(string='Ref Supplier')
