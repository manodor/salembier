# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    category_code = fields.Char(string='Code', )