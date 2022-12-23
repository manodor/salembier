
from odoo import fields, models, api, _


class PartnerCategory(models.Model):
    _name = 'partner.category'

    name = fields.Char("Name", required=True)
    parent_id = fields.Many2one('partner.category', 'Parent')

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValueError(_('Error ! You cannot create recursive categories.'))

