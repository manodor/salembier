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

    @api.model
    def create(self, values):

        res = super(SaleOrder, self).create(values)

        grouping_family_qty = {}
        grouping_family_product = {}
        for line in res.order_line:
            if line.display_type not in ('line_section', 'line_note'):
                if line.product_id.categ_family_gruping.id in grouping_family_product:
                    grouping_family_qty[line.product_id.categ_family_gruping.id] += line.product_uom_qty
                else:
                    grouping_family_qty[line.product_id.categ_family_gruping.id] = line.product_uom_qty
                    grouping_family_product[line.product_id.categ_family_gruping.id] = line.product_id

        for record in grouping_family_product:
            for line in res.order_line:
                if line.display_type not in ('line_section', 'line_note'):
                    qty_save = line.product_uom_qty
                    line.product_uom_qty = grouping_family_qty[record]

                    if line.order_id.pricelist_id and line.order_id.partner_id:
                        product = line.product_id.with_context(
                            lang=line.order_id.partner_id.lang,
                            partner=line.order_id.partner_id,
                            quantity=grouping_family_qty[record],
                            date=line.order_id.date_order,
                            pricelist=line.order_id.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=self.env.context.get('fiscal_position')
                        )
                        line.price_unit = product._get_tax_included_unit_price(
                            line.company_id or line.order_id.company_id,
                            line.order_id.currency_id,
                            line.order_id.date_order,
                            'sale',
                            fiscal_position=line.order_id.fiscal_position_id,
                            product_price_unit=line._get_display_price(product),
                            product_currency=line.order_id.currency_id
                        )

                    line.product_uom_qty = qty_save

        return res

    def write(self, values):

        res = super(SaleOrder, self).write(values)

        grouping_family_qty = {}
        grouping_family_product = {}
        for line in self.order_line:
            if line.display_type not in ('line_section', 'line_note'):
                if line.product_id.categ_family_gruping.id in grouping_family_product:
                    grouping_family_qty[line.product_id.categ_family_gruping.id] += line.product_uom_qty
                else:
                    grouping_family_qty[line.product_id.categ_family_gruping.id] = line.product_uom_qty
                    grouping_family_product[line.product_id.categ_family_gruping.id] = line.product_id

        _logger.info('group 1 %r', grouping_family_product)
        for record in grouping_family_product:
            for line in self.order_line:
                if line.display_type not in ('line_section', 'line_note'):
                    qty_save = line.product_uom_qty
                    line.product_uom_qty = grouping_family_qty[record]

                    if line.order_id.pricelist_id and line.order_id.partner_id:
                        product = line.product_id.with_context(
                            lang=line.order_id.partner_id.lang,
                            partner=line.order_id.partner_id,
                            quantity=grouping_family_qty[record],
                            date=line.order_id.date_order,
                            pricelist=line.order_id.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=self.env.context.get('fiscal_position')
                        )
                        _logger.info('group 2 %r', product)
                        _logger.info('group 3 %r', line.price_unit)
                        line.price_unit = product._get_tax_included_unit_price(
                            line.company_id or line.order_id.company_id,
                            line.order_id.currency_id,
                            line.order_id.date_order,
                            'sale',
                            fiscal_position=line.order_id.fiscal_position_id,
                            product_price_unit=line.price_unit,
                            product_currency=line.order_id.currency_id
                        )
                        _logger.info('group 4 %r', line.price_unit)

                    line.product_uom_qty = qty_save
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
