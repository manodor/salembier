from odoo import api, fields, models, tools, SUPERUSER_ID, _


class StockWarehouseOrderPoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    current_rule = fields.Boolean("Current Rule", default=True)
