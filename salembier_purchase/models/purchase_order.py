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
                if filter:
                    self.product_supplier_ref = filter.product_code
                    self.name = filter.product_name
            else:
                filter = self.product_id.seller_ids.filtered(
                    lambda r: r.name == self.order_id.partner_id and r.product_id == self.product_id)
                if filter:
                    self.product_supplier_ref = filter.product_code
                    self.name = filter.product_name

    product_supplier_ref = fields.Char(string='Ref Supplier')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def update_product_price(self):
        partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
        for line in self.order_line:
            if line.product_id.type in ['product', 'consu', 'service']:
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                supplier_price = currency._convert(line.price_unit, currency, self.env.company, line.date_order or fields.Date.today(), round=False)
                price = self.currency_id._convert(line.price_unit, self.company_id.currency_id, line.company_id,
                                                  line.date_order or fields.Date.today(), round=False)

                seller = line.product_id._select_seller(
                    partner_id=partner,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    seller.write({'price': supplier_price})

                line.product_id.standard_price = price
