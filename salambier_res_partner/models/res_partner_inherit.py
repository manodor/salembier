# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
import logging

log = logging.getLogger(__name__).info


class ResPartnerInheritance(models.Model):
    _inherit = "res.partner"

    mt_franco = fields.Integer("mt franco")
    mt_mini_cde = fields.Integer("Mt mini cde")
    taux_escompte = fields.Integer("Taux Escompte")
    sous_escompte = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ], 'Sous Escompte')
    phone_exist = fields.Boolean(string='phone exist', compute='get_phone_exist')
    # customer
    soumis_tva = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ], 'Soumis ou non a la TVA')
    podo = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ], 'Podo/Spécifique')
    enseigne = fields.Char("Enseigne")
    leads = fields.Boolean(string="Prospect", default=True)

    def name_get(self):
        if self._context.get('adress'):
            result = []
            for partner in self:
                name = partner.street
                result.append((partner.id, name))
            return result
        else:
            return super(ResPartnerInheritance, self).name_get()

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('partner_show_db_id'):
            name = "%s (%s)" % (name, partner.id)
        if self._context.get('address_inline'):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get('show_email') and partner.email:
            name = "%s \n %s" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        if self._context.get('show_phone') and partner.phone:
            name = "%s \n %s" % (name, partner.phone)
        if self._context.get('show_mobile') and partner.mobile:
            name = "%s \n %s" % (name, partner.mobile)
        return name

    @api.depends('phone', 'mobile')
    def get_phone_exist(self):
        for rec in self:
            if rec.phone or rec.mobile:
                rec.phone_exist = True
            else:
                rec.phone_exist = False

    @api.model
    def create(self, values):
        if self.env.user.id != SUPERUSER_ID and not self.user_has_groups('salambier_res_partner.group_create_partner'):
            raise UserError(_("You do not have the rights to create partner."))
        res = super(ResPartnerInheritance, self).create(values)
        if res.parent_id:
            res.leads = res.parent_id.leads
        return res

    def write(self, values):

        res = super(ResPartnerInheritance, self).write(values)
        if 'leads' in values:
            for record in self:
                contact_ids = self.env['res.partner'].search([('parent_id', '=', record.id)])
                if contact_ids:
                    contact_ids.write({'leads': values['leads']})
        return res

    def copy(self, default=None):
        default = default or {}
        if self._needs_ref():
            if self._context.get('default_customer_rank'):
                default["ref"] = self._get_next_ref_customer()
        return super(ResPartnerInheritance, self).copy(default=default)

    @api.onchange('property_account_position_id')
    def onchange_property_account_position_id(self):
        if self.property_account_position_id:
            self.soumis_tva = self.property_account_position_id.soumis_tva

    # script pour modifier
    def update_payment_condition(self):
        partner_ids = self.env['res.partner'].search([('supplier_rank', '>', 0)])
        for partner in partner_ids:
            if partner.property_payment_term_id:
                partner.write({'property_supplier_payment_term_id': partner.property_payment_term_id.id,
                               'property_payment_term_id': False})

