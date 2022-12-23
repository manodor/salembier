# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    soumis_tva = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ], 'Soumis ou non a la TVA')