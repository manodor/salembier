# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    account_serial_number = fields.Char(string='Serial Number', required=False, store=True)
    account_serial_number_html = fields.Html(string='Serial Number', required=False, store=True)