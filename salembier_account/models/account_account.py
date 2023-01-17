# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    def add_chart_of_account(self):
        account = self.env['account.account'].search([])
        for rec in account:
            if len(rec.code) <= 6 and rec.group_id and rec.group_id.id not in [87,82]:
                code = rec.code + '00'
                if code not in account.mapped('code'):
                    rec.code = code