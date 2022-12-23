from odoo import models, fields, api, _
import binascii
import tempfile
import xlrd
import base64

import logging

logger = logging.getLogger(__name__)


class SupplierPriceImport(models.TransientModel):
    _name = 'supplier.price.import'

    import_file = fields.Binary("Import File")

    def import_supplier_price(self):
        text_to_import = base64.decodebytes(self.import_file)
        workbook = xlrd.open_workbook(file_contents=text_to_import)
        sheet = workbook.sheet_by_index(0)
        for row in range(1, sheet.nrows):
            # get the column name from the first row
            product = self.env['product.product'].search([('default_code', '=', sheet.cell_value(row, 0))], limit=1)
            supplierinfo = self.env['product.supplierinfo'].search([('product_id', '=', product.id)], limit=1)
            currency_id = self.env['res.currency'].search([('name', '=', sheet.cell_value(row, 31))], limit=1)
            supplier_ref = sheet.cell_value(row, 49)
            supplier_description = sheet.cell_value(row, 50)
            if currency_id:
                currency_id = currency_id.id
            else:
                currency_id = 1
            if not product:
                continue
            if product:
                supplierinfo.write({
                    'price': sheet.cell_value(row, 33),
                    'currency_id': currency_id,
                    'current_vendor': True,
                    'product_code': supplier_ref,
                    'product_name': supplier_description,
                })
        return True