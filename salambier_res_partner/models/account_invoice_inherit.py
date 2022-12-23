# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class FacturationcetAccountInvoice (models.Model):
      _inherit = "account.move"

      @api.onchange('partner_id', 'invoice_line_ids')
      def get_tax_vendor(self):
          if self.partner_id.sous_escompte == 'non':
              for line in self.invoice_line_ids:
                  line.tax_ids = [(5,0,0)]
