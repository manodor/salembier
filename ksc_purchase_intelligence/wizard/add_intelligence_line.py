from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class AddIntelligenceLine(models.TransientModel):
    _name = 'add.intelligence.line'

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
    product_topology = fields.Selection(string='Product topology',
                                        selection=[('conso', 'CONSO'),
                                                   ('gm', 'GM'),
                                                   ('sav', 'SAV')])

    @api.model
    def default_get(self, fields):
        res = super(AddIntelligenceLine, self).default_get(fields)
        if self._context.get('active_id'):
            res.update({'vendor_id': self._context.get('default_vendor_id')})
        return res

    @api.depends('max_qty', 'forecasted_qty')
    def _get_purchase_qty(self):
        for rec in self:
            rec.purchase_qty = rec.max_qty - rec.forecasted_qty

    @api.onchange('product_id')
    def onchange_product(self):
        reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', self.product_id.id),
                                                                      ('current_rule', '=', True)], limit=1)
        packaging = self.env['product.packaging'].search([('product_id', '=', self.product_id.id),
                                                          ('purchase', '=', True)], limit=1)
        supplier = self.env['product.supplierinfo'].search([('id', 'in', self.product_id.seller_ids.ids),
                                                            ('current_vendor', '=', True)], limit=1)
        self.update({
            'qty_packaging': packaging.qty,
            'min_qty': reorder_rule.product_min_qty,
            'max_qty': reorder_rule.product_max_qty,
            'product_topology': self.product_id.product_topology,
        })

    def get_packaging_qty(self, product_id):
        packaging = product_id.packaging_ids.filtered(lambda p: p.purchase)
        return packaging[0].qty if packaging else 0

    def create_intelligence_rec(self):
        purchase_intelligence = self.env['purchase.intelligence'].search([])
        product_exist = purchase_intelligence.mapped('product_id')
        supplier_price_list = self.env['product.supplierinfo'].search([('name', '=', self.vendor_id.id),
                                                            ('current_vendor', '=', True)])
        if not self.product_id and self.vendor_id:
            self.env['purchase.intelligence'].search([]).unlink()
            for line in supplier_price_list:
                #reorder_rule = self.env['stock.warehouse.orderpoint'].search(['|',('product_id', '=', supplier.product_id.id),'&',('product_id', '=', supplier.product_id.id),('current_rule', '=', True)], limit=1)
                if line.product_id:
                    reorder_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', line.product_id.id)], limit=1)
                    purchase_qty = reorder_rule.product_max_qty - line.product_id.virtual_available
                    if purchase_qty < 0:
                        purchase_qty = 0
                    self.env['purchase.intelligence'].create({
                        'product_id': line.product_id.id,
                        #'qty_packaging': line.product_id.qty_packaging,
                        'min_qty': reorder_rule.product_min_qty,
                        'max_qty': reorder_rule.product_max_qty,
                        'vendor_id': self.vendor_id.id,
                        'qty_packaging': self.get_packaging_qty(line.product_id),
                        'purchase_qty': purchase_qty,
                    })
                else:
                    if len(line.product_tmpl_id.product_variant_ids) == 1:
                        product = line.product_tmpl_id.product_variant_ids[0]
                        reorder_rule = self.env['stock.warehouse.orderpoint'].search(
                            [('product_id', '=', product.id)], limit=1)
                        purchase_qty = reorder_rule.product_max_qty - product.virtual_available
                        if purchase_qty < 0:
                            purchase_qty = 0
                        self.env['purchase.intelligence'].create({
                            'product_id': product.id,
                            #'qty_packaging': product.qty_packaging,
                            'min_qty': reorder_rule.product_min_qty,
                            'max_qty': reorder_rule.product_max_qty,
                            'vendor_id': self.vendor_id.id,
                            'qty_packaging': self.get_packaging_qty(product),
                            'purchase_qty': purchase_qty,
                        })
        else:
            if self.product_id in product_exist:
                raise ValidationError("Product already exist in the list")
            elif not self.product_id:
                raise ValidationError("Please select a product")
            else:
                self.env['purchase.intelligence'].create({
                    'product_id': self.product_id.id,
                    'qty_packaging': self.qty_packaging,
                    'min_qty': self.min_qty,
                    'max_qty': self.max_qty,
                    'vendor_id': self.vendor_id.id,
                    'purchase_qty': self.purchase_qty,
                })

    @api.onchange('product_id', 'vendor_id')
    def filter_product(self):
        product_supplier = self.env['product.supplierinfo'].search([('name', '=', self.vendor_id.id)])
        product_list = []
        if not product_supplier:
            raise ValidationError(
                _('Please first define product for this vendor'))
        for rec in product_supplier:
            if rec.product_id:
                product_list.append(rec.product_id.id)
            else:
                product = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_tmpl_id.id)],
                                                             limit=1)
                product_list.append(product.id)
        return {'domain': {'product_id': [('id', 'in', product_list)]}}
