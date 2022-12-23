# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields,api, _, exceptions
import csv
import io
from odoo.exceptions import Warning, ValidationError
import base64
import tempfile
from tempfile import TemporaryFile
import binascii

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
    
class wizard_import(models.TransientModel):
    _name = 'wizard.import'

    file = fields.Binary('Select File', help='select file')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    
    
    sample_option = fields.Selection([('csv', 'CSV'),('xls', 'XLS')],string='Sample Type',default='csv')
    down_samp_file = fields.Boolean(string='Download Sample Files')
    
    
    def make_reordering_rules(self, values):
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        prod_obj = self.env['product.product']
        search_prod = prod_obj.search([('default_code', '=', values['product_code'])], limit=1)
        if search_prod:
            new_rule = orderpoint_obj.create({'product_id' : search_prod.id,
                           'product_min_qty': float(values['min_rule']),
                           'product_max_qty': float(values['max_rule']),
                           'current_rule': values['current'],
                                })
        else:
            pass
            #raise ValidationError(_('"%s" There is no product code in system.') % values.get('product_code'))
        return True
    
    def import_button(self):

        if self.import_option == 'csv':
            keys=['product_code', 'min_rule','max_rule']
            
            try:
                attachment = base64.b64decode(self.file)
                file_input = io.StringIO(attachment.decode("utf-8"))
                file_input.seek(0)
                file_reader = []
                csv_reader = csv.reader(file_input, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.ValidationError(_("Invalid file!"))
            
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.make_reordering_rules(values)
        else:
            try:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_("Invalid file!"))
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    code = line[0]
                    values.update({'product_code': code,
                                    'min_rule': line[1],
                                    'max_rule': line[2],
                                    'current': line[3],
                                    })
                    res = self.make_reordering_rules(values)
        return res
    
    
    def download_auto(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_document?model=wizard.import&id=%s'%(self.id),
             'target': 'new',
             }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
