from odoo import models, fields, api, _
import binascii
import tempfile
import xlrd
import base64

import logging

logger = logging.getLogger(__name__)


class ImportProductVariants(models.TransientModel):
    _name = 'import.product.packaging'

    import_file = fields.Binary("Import File")

    def import_product_packaging(self):
        text_to_import = base64.decodebytes(self.import_file)
        workbook = xlrd.open_workbook(file_contents=text_to_import)
        sheet = workbook.sheet_by_index(0)
        for row in range(3, sheet.nrows):
            product = self.env['product.product'].search([('default_code', '=', sheet.cell_value(row, 0))], limit=1)
            if not product:
                continue
            if product:
                if sheet.cell_value(row, 18) == 1 and sheet.cell_value(row, 19) != 0:
                    package = self.env['product.packaging'].create({
                        'product_id': product.id,
                        'name': product.name,
                        'qty': sheet.cell_value(row, 19),
                        'sales': True,
                        'purchase': False,
                    })
                if sheet.cell_value(row, 16) == 1 and sheet.cell_value(row, 17) != 0:
                    package = self.env['product.packaging'].create({
                        'product_id': product.id,
                        'name': product.name,
                        'qty': sheet.cell_value(row, 17),
                        'sales': False,
                        'purchase': True,
                    })
        return True
