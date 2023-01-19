from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class PurchaseIntelligence(models.Model):
    _name = 'purchase.intelligence'

    product_id = fields.Many2one("product.product", "Product Name")
    name = fields.Char("Name", related="product_id.name")
    ref = fields.Char("Reference", related="product_id.default_code")
    forecasted_qty = fields.Float("Forecasted Quantity", related="product_id.virtual_available")
    qty_packaging = fields.Float("Packaging Quantity")
    min_qty = fields.Float("Min Qty")
    max_qty = fields.Float("Max Qty")
    vendor_id = fields.Many2one("res.partner", "Current vendor")
    onhand_qty = fields.Float("Onhand Qty", related="product_id.qty_available")
    incoming_qty = fields.Float("Incoming Qty", related="product_id.incoming_qty")
    outgoing_qty = fields.Float("Outgoing Qty", related="product_id.outgoing_qty")
    purchase_qty = fields.Float("Purchase Qty", compute="_get_purchase_qty", readonly=False, store=True)
    static = fields.Char("Stats N-1", related="product_id.static")
    product_topology = fields.Selection("Product Topology", related="product_id.product_topology")
    number_of_coli = fields.Float("Number of Coli", compute="_get_number_of_coli", store=True)
    reorder_rule_id = fields.Many2one("stock.warehouse.orderpoint", string="Reordering rule")

    def get_description_product(self, rec):
        product_description = False
        product_supplier_ref = False
        if rec.product_id:
            if len(rec.product_id.variant_seller_ids) == 1:
                filter = rec.product_id.variant_seller_ids.filtered(
                    lambda r: r.name == rec.vendor_id)
                if filter:
                    product_supplier_ref = filter.product_code
                    product_description = filter.product_name
                    price = filter.price
                else:
                    product_supplier_ref = rec.product_id.default_code
                    product_description = rec.product_id.display_name
                    price = rec.product_id.standard_price
            else:
                filter = rec.product_id.seller_ids.filtered(
                    lambda r: r.name == rec.vendor_id and r.product_id == rec.product_id)
                if filter:
                    product_supplier_ref = filter.product_code
                    product_description = filter.product_name
                    price = filter.price
                else:
                    product_supplier_ref = rec.product_id.default_code
                    product_description = rec.product_id.display_name
                    price = rec.product_id.standard_price
        return product_supplier_ref, product_description, price

    @api.depends('max_qty', 'forecasted_qty', 'reorder_rule_id.qty_multiple')
    def _get_purchase_qty(self):
        for rec in self:
            rec.purchase_qty = (rec.max_qty - rec.forecasted_qty) * rec.reorder_rule_id.qty_multiple if rec.reorder_rule_id and rec.reorder_rule_id.qty_multiple > 0 else 0.0
            if rec.purchase_qty < 0:
                rec.purchase_qty = 0

    @api.depends('purchase_qty', 'qty_packaging')
    def _get_number_of_coli(self):
        for rec in self:
            rec.number_of_coli = rec.purchase_qty / rec.qty_packaging if rec.qty_packaging > 0 else 1

    def action_purchase_intelligence(self):
        self.search([]).unlink()
        products = self.env['product.product'].search([('product_comment', '=', False), ('rent_ok', '=', False)])
        for product in products:
            reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id),
                                                                          ('current_rule', '=', True)], limit=1)
            if reorder_rule and product.virtual_available <= reorder_rule.product_min_qty:
                packaging = self.env['product.packaging'].search([('product_id', '=', product.id),
                                                                  ('purchase', '=', True)], limit=1)
                supplier = self.env['product.supplierinfo'].search([('id', 'in', product.seller_ids.ids),
                                                                    ('current_vendor', '=', True)], limit=1)
                self.create({
                    'product_id': product.id,
                    'qty_packaging': packaging.qty,
                    'min_qty': reorder_rule.product_min_qty,
                    'max_qty': reorder_rule.product_max_qty,
                    'vendor_id': supplier.name.id,
                    'reorder_rule_id': reorder_rule.id,
                })
            context = {'search_default_topology': 1}
        return {
            "name": _("Purchase Intelligence"),
            "view_mode": "tree",
            "res_model": "purchase.intelligence",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": context,
        }

    def create_purchase_order(self):
        if self._context.get('skip_wizard'):
            for rec in self:
                if rec.vendor_id:
                    purchase_order = self.env['purchase.order'].search([('partner_id', '=', rec.vendor_id.id),
                                                                        ('state', '=', 'draft')], limit=1,
                                                                       order="id desc")
                    code , name, price = self.get_description_product(rec)
                    if purchase_order:
                        self.env['purchase.order.line'].create({
                            'product_supplier_ref': code,
                            'name': name,
                            'product_qty': rec.purchase_qty,
                            'product_id': rec.product_id.id,
                            'product_uom': rec.product_id.uom_po_id.id,
                            'price_unit': price,
                            'date_planned': fields.Date.today(),
                            'order_id': purchase_order.id,
                        })
                    else:
                        line_vals = {
                            'product_supplier_ref': code,
                            'name': name,
                            'product_qty': rec.purchase_qty,
                            'product_id': rec.product_id.id,
                            'product_uom': rec.product_id.uom_po_id.id,
                            'price_unit': price,
                            'date_planned': fields.Date.today(),
                        }
                        if not rec.vendor_id.property_purchase_currency_id.id:
                            raise UserError(_("Please set the currency for the vendor %s") % rec.vendor_id.name)
                        purchase = self.env['purchase.order'].create({
                            'partner_id': rec.vendor_id.id,
                            'user_id': self.env.user.id,
                            'origin': 'Achat Intelligent',
                            'company_id': self.env.company.id,
                            'currency_id': rec.vendor_id.property_purchase_currency_id.id,
                            'payment_term_id': rec.vendor_id.with_company(
                                self.env.company).property_supplier_payment_term_id.id,
                            'date_order': fields.Date.today(),
                            'order_line': [(0, 0, line_vals)],

                        })
        else:
            return {
                'name': 'Confirm Box',
                'res_model': 'confirm.box',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'context': {
                    "default_intelligence_ids": [(6, 0, self.ids)],
                },
                'target': 'new',
            }

    def add_new_lines(self):
        suppplier_info = self.env['product.supplierinfo'].search([('name', 'in', self.mapped('vendor_id').ids)])
        product = suppplier_info.product_tmpl_id.mapped("product_variant_id")
        active_id = self.env.context.get('active_id')
        return {
            'name': 'Add Intelligence Line',
            'res_model': 'add.intelligence.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {
                "product": product.ids,
                "default_vendor_id": self.vendor_id.id,
                "active_id": active_id,
            },
            'target': 'new',
        }
