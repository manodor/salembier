from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def update_product_price(self):
        partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
        for line in self.order_line:
            currency = partner.property_purchase_currency_id or self.env.company.currency_id
            supplier_price = currency._convert(line.price_unit, currency, self.env.company, line.date_order or fields.Date.today(), round=False)

            price = self.currency_id._convert(line.price_unit, self.company_id.currency_id, line.company_id,
                                              line.date_order or fields.Date.today(), round=False)

            supplier_rec = self.env['product.supplierinfo'].search([('name', '=', self.partner_id.id),
                                                                    ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                                    ('current_vendor', '=', True)])
            if supplier_rec:
                supplier_rec = supplier_rec.filtered(lambda r: r.product_id == line.product_id)

            for seller in supplier_rec:
                seller.price = supplier_price
            line.product_id.standard_price = price
