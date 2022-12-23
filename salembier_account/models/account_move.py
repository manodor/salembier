# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one('sale.order', compute='_compute_sale_order', store=True)

    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_order(self):
        for rec in self:
            rec.sale_order_id = rec.mapped('invoice_line_ids.sale_line_ids.order_id')

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        res = super(AccountMove, self).action_invoice_sent()

        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)

        template.attachment_ids = [(5, 0, 0)]
        report_id = 'stock.action_report_delivery'
        
        for pick in self.sale_order_id.mapped('picking_ids'):
            data, data_format = self.env.ref(report_id)._render_qweb_pdf(pick.id)
            b64_pdf = base64.b64encode(data)

            attachment_name = 'Bon de livraison - %s' % pick.name + '.pdf'

            attachment_picking_id = self.env['ir.attachment'].create({
                'name': attachment_name,
                'type': 'binary',
                'datas': b64_pdf,
                'store_fname': attachment_name,
                'res_model': 'stock.picking',
                'res_id': pick.id,
                'mimetype': 'application/pdf',
            })


            template.attachment_ids = [(4, attachment_picking_id.id)]

        return res