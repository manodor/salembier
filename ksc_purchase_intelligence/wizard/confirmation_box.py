from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ConfirmBox(models.TransientModel):
    _name = 'confirm.box'

    yes_no = fields.Char(default='Do you want to Create Purchase Order?')
    intelligence_ids = fields.Many2many("purchase.intelligence", string="Purchase Intelligence")

    def yes(self):
        self.intelligence_ids.with_context(skip_wizard=1).create_purchase_order()
