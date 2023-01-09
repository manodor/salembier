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

    def delete_price_supplier_info(self):
        deleted_list = []
        product = self.env['product.template'].search([])
        product_supplierinfo = self.env['product.supplierinfo'].search([])
        for line in product:
            if line.product_variant_count > 1:
                for rec in product_supplierinfo:
                    if rec.product_tmpl_id.id == line.id:
                        print(rec.product_tmpl_id.name)
                        if not rec.product_id:
                            deleted_list.append(rec.id)
        self.env['product.supplierinfo'].browse(deleted_list).unlink()



