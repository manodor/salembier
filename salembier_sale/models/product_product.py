# -*- coding: utf-8 -*-
import re

from odoo import fields, models, api
import xlrd


class ProductProduct(models.Model):
    _inherit = "product.product"

    marge_product = fields.Float(string='Marge', compute='product_marge_compute')
    marge_product_percentage = fields.Float(string='Marge percentage', compute='product_marge_compute')
    marge_product_coef = fields.Float(string='Coef de marge', compute='product_marge_compute')
    margin_fixed = fields.Float(string='Marge Théorique fixe', )
    impact_of_additional_cost = fields.Monetary(string="Impact of Additional Cost")
    transportation = fields.Float(string="Transportation")
    real_cost = fields.Float(string="Real Cost", compute="_get_real_cost")
    product_name = fields.Char("Name")
    static = fields.Char(string='Stats N-1', required=False)
    categ_family_gruping = fields.Many2one('product.grouping.family', string='Grouping Family', index=True)
    product_obsolete = fields.Boolean(string='produit obsolète')
    recall = fields.Boolean(string='Récylum')

    # script to add the product_name from product_template to product_product
    def replace_name_product(self):
        product_product = self.env['product.product']
        for product in product_product.search([]):
            if not product.product_name:
                product.write({'product_name': product.product_tmpl_id.name})

    @api.depends('list_price', 'seller_ids')
    def product_marge_compute(self):
        for rec in self:
            if rec.list_price:
                rec.marge_product = rec.list_price - rec.real_cost
                if rec.list_price > 0:
                    rec.marge_product_percentage = (rec.marge_product * 100) / rec.list_price
                else:
                    rec.marge_product_percentage = 0
                if rec.real_cost > 0:
                    rec.marge_product_coef = rec.list_price / rec.real_cost
                else:
                    rec.marge_product_coef = 0
            else:
                rec.marge_product = 0
                rec.marge_product_percentage = 0
                rec.marge_product_coef = 0

    @api.depends('impact_of_additional_cost', 'transportation', 'seller_ids')
    def _get_real_cost(self):
        for rec in self:
            current_vendor = rec.seller_ids.filtered(lambda r: r.current_vendor)
            for vendor in current_vendor:
                if vendor:
                    current_vendor_price = vendor.currency_id._convert(vendor[0].price, self.env.company.currency_id,
                                                                               self.env.company, fields.Date.today())
            transportation = (rec.standard_price * rec.transportation) / 100
            rec.real_cost = rec.standard_price + rec.impact_of_additional_cost + transportation


    """This code is script to import variant"""

    def get_product_id(self, cell_value):
        product = self.env['product.template'].search([('default_code', '=', cell_value)])
        if product:
            return product.id
        return False

    def get_attribute_id(self, cell_value):
        product_attribute = self.env['product.attribute'].search([('name', '=', str(cell_value))])
        if product_attribute:
            return product_attribute.id
        return False

    def get_attribute_value(self, cell_value, attribute_id):
        attribute_value = []
        product_attribute_value = self.env['product.attribute.value'].search([('name', '=', str(cell_value))])
        if product_attribute_value:
            attribute_value.append(product_attribute_value.id)
        else:
            new_value = self.env['product.attribute.value'].create({'name': str(cell_value),
                                                                    'attribute_id': attribute_id})
            attribute_value.append(new_value.id)
        return [(6, 0, attribute_value)]

    def get_value(self, row, first_sheet):
        list_value = []
        for col in range(6, 15):
            attribute_id = self.get_attribute_id(first_sheet.cell(0, col).value)
            if self.get_attribute_id(first_sheet.cell(0, col).value) and self.get_attribute_value(first_sheet.cell(row, col).value, attribute_id):

                value = {'attribute_id': self.get_attribute_id(first_sheet.cell(0, col).value),
                         'value_ids': self.get_attribute_value(first_sheet.cell(row, col).value, attribute_id)}
                list_value.append((0, 0, value))
        return list_value

    def import_variant(self):
        product_product = self.env['product.product']
        file_path = str(self.env['ir.config_parameter'].get_param('product_variant_import_path'))
        if file_path:
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            for row in range(1, first_sheet.nrows):
                product_id = self.get_product_id(first_sheet.cell(row, 4).value)
                print("product_id", product_id)
                if product_id:
                    if self.get_value(row, first_sheet):
                        variant_create = product_product.create({'name': first_sheet.cell(row, 1).value,
                                                                 'product_topology': 'conso',
                                                                 'product_tmpl_id': self.get_product_id(
                                                                     first_sheet.cell(row, 4).value),
                                                                 'default_code': first_sheet.cell(row, 0).value,
                                                                 'attribute_line_ids': self.get_value(row, first_sheet),
                                                                })

    """This code is script to add descriptin to product"""
    def get_description(self):
        product = self.env['product.template'].search([])
        for rec in product:
            if rec.description:
                # delete tags from rec.description
                description = re.sub('<[^<]+?>', '', rec.description)
                rec.description_sale = description


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    current_vendor = fields.Boolean("Current Vendor")
