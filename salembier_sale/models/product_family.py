# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductFamily(models.Model):
    _name = 'product.family'
    _description = 'Product Family'

    name = fields.Char('Name', )
    code = fields.Char(string='Code')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """ search full name and code """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)