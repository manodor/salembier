# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def filter_product(self):
        if self.env.user.has_group('product_filter_by_vendor.group_product_filter_user'):
            product_supplier = self.env['product.supplierinfo'].search([('name','=',self.partner_id.id)])
            product_list =[]
            if not product_supplier:
                raise ValidationError(_('Please first define product for this vendor in Purchase -> Configuration -> Vendor Pricelists'))
            for rec in product_supplier:
                if rec.product_id:
                    product_list.append(rec.product_id.id)
                else:
                    product = self.env['product.product'].search([('product_tmpl_id','=',rec.product_tmpl_id.id)], limit=1)
                    product_list.append(product.id)
            # search service product type
            service_product = self.env['product.product'].search([('type','=','service')])
            for rec in service_product:
                product_list.append(rec.id)
            return {'domain': {'product_id': [('id', 'in', product_list)]}}
