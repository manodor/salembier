from odoo import models , fields , api

import logging

_logger = logging.getLogger(__name__)


class SaleOrderCetInheritance (models.Model):
      _inherit = "sale.order"

      @api.onchange('partner_id', 'order_line')
      def get_tax_vendor(self):
          if self.partner_id.sous_escompte == 'non':
              for line in self.order_line:
                  line.tax_id = [(5,0,0)]
                  _logger.info("IT IS INFO" )