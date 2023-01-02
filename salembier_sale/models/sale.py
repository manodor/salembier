# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_due = fields.Monetary(string='Montant dû', related='partner_id.total_due', readonly=True)
    related_category_id = fields.Many2many(related='partner_id.category_id')

    def action_confirm(self):
        if self.partner_id.leads:
            raise UserError(
                _("You can not confirm this order because the customer has leads")
            )
        for line in self.order_line:
            if line.product_id.product_obsolete:
                available_qty = line.product_id.with_context({'warehouse_id': self.warehouse_id}).qty_available
                if available_qty < line.product_uom_qty:
                    raise UserError(_("Make sure you have the quantities available in stock (obsolete product): %s", line.product_id.name))
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.onchange('order_line.product_uom_qty')
    def qty_obsolete_raise(self):
        for line in self.order_line:
            print('yes inside the change')
            if line.product_id.product_obsolete:
                available_qty = line.product_id.with_context({'warehouse_id': self.warehouse_id}).qty_available
                if available_qty < line.product_uom_qty:
                    raise UserError(_("Make sure you have the quantities available in stock (obsolete product): %s",
                                      line.product_id.name))
    """Code for the grouping family total price """
    def _get_search_vals_for_quantity(self, line):
        return [
            ('order_id', '=', line.order_id.id),
            ('state', '!=', 'cancel'),
            ('product_id.categ_family_gruping', '=', line.product_id.categ_family_gruping.id),
        ]

    def _get_quantity_to_compute(self, line):
        quantity = line.product_uom_qty
        if line.product_id:
            order_line_obj = self.env['sale.order.line']
            search_domain = self._get_search_vals_for_quantity(line)
            line_ids = order_line_obj.search(search_domain)
            quantity = sum([x.product_uom_qty for x in line_ids])
        return quantity

    def _get_price_of_line(self, product_id,
                           qty, partner_id, pricelist_id):
        return pricelist_id._compute_price_rule_multi(
            products_qty_partner=[(product_id, qty, partner_id)])

    def _check_if_edit(self, res, product_id):
        if res.get(product_id):
            vals = res.get(product_id, False)
            # get the 2nd item of the tuple
            item_id = vals[2][1]
            if item_id:
                item = self.env['product.pricelist.item'].browse(item_id)
                if item.grouping_family_id:
                    return True
        return False

    def _get_child_pricelist(self, res):
        if res.get('item_id'):
            item_id = res.get('item_id', False)
            if item_id:
                item = self.env['product.pricelist.item'].browse(item_id)
                if item.base_pricelist_id:
                    return item.base_pricelist_id
        return False

    def compute_global_discount(self):
        for sale in self:
            if sale.state in ['draft', 'sent']:
                sale.order_line.compute_global_discount()
        return True

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        res.compute_global_discount()
        return res

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        self.compute_global_discount()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pu_net = fields.Float(string='PU NET', digits=(16, 2), compute='compute_amount_remise')
    pu_discount = fields.Float(string='PU TTC Rem', digits=(16, 2), compute='compute_amount_remise')
    pu_ttc = fields.Float(string='PU TTC', digits=(16, 2), compute='compute_price_pu_ttc')
    amount_ttc = fields.Float(string='Amount TTC', digits=(16, 2), compute='compute_price_ttc')

    @api.depends('price_unit', 'discount', 'pu_ttc', 'amount_ttc')
    def compute_amount_remise(self):
        for line in self:
            line.pu_net = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.discount == 0:
                line.pu_discount = line.pu_ttc
            else:
                line.pu_discount = line.pu_ttc - (line.pu_ttc * (line.discount / 100))

    @api.depends('price_unit', 'tax_id')
    def compute_price_pu_ttc(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, 1,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            taxes_price = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            line.pu_ttc = line.price_unit + taxes_price

    @api.depends('price_subtotal', 'tax_id')
    def compute_price_ttc(self):
        for line in self:
            line.amount_ttc = line.price_subtotal + line.price_tax

    @api.onchange('product_uom_qty')
    def qty_obsolete_raise(self):
        for line in self:
            if line.product_id.product_obsolete:
                available_qty = line.product_id.with_context({'warehouse_id': self.warehouse_id}).qty_available
                if available_qty < line.product_uom_qty:
                    raise UserError(_("Make sure you have the quantities available in stock (obsolete product): %s",
                                      line.product_id.name))

    def _update_description(self):
        result = super(SaleOrderLine, self)._update_description()
        name = ''
        if self.product_id.product_name and self.product_id.description_sale:
            name = self.product_id.product_name + " \n " + self.product_id.description_sale
        elif self.product_id.product_name:
            name = self.product_id.product_name
        elif self.product_id.description_sale:
            name = self.product_id.description_sale
        elif self.product_id.product_tmpl_id:
            name = self.product_id.product_tmpl_id.name
        self.update({'name': name})

    def compute_global_discount(self):
        for line in self:
            sale = line.order_id.with_context(date=line.order_id.date_order)
            partner_id = sale.partner_id.id
            if line.product_id:
                pricelist_id = sale.pricelist_id
                product_id = line.product_id
                qty = sale._get_quantity_to_compute(line)
                if qty:
                    res = sale._get_price_of_line(
                        product_id, qty, partner_id, pricelist_id)
                    while True:
                        new_pricelist_id = sale._get_child_pricelist(res)
                        if not new_pricelist_id:
                            break
                        res = sale._get_price_of_line(product_id,
                                                      qty, partner_id,
                                                      new_pricelist_id)
                        pricelist_id = new_pricelist_id
                    price_unit = False
                    if sale._check_if_edit(res, line.product_id.id):
                        price_unit = res.get(
                            line.product_id.id)[2][0]
                        print(price_unit)
                    else:
                        price_unit = pricelist_id.with_context(
                            date=line.order_id.date_order).price_get(
                            product_id.id, line.product_uom_qty,
                            partner=sale.partner_id.id)[pricelist_id.id]
                    if price_unit is not False:
                        line.write({'price_unit': price_unit})
        return True
