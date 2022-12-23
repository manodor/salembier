from odoo import api, fields, models
from odoo.exceptions import AccessError


class Product(models.Model):
    _inherit = "product.product"

    def name_get(self):
        if self.env.context.get('purchase'):
            return [
                (r.id, "[{code}] {name}".format(code=r.default_code, name=r.product_name)) for r in self
            ]
        return super(Product, self).name_get()
