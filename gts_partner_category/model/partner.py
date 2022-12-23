
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    group_category_id = fields.Many2one('partner.category', string="Category")
