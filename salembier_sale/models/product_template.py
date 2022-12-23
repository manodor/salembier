# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_comment = fields.Boolean(string='Comment', required=False, copy=True)
    product_topology = fields.Selection(string='Product topology',
                                        selection=[('conso', 'CONSO'),
                                                   ('gm', 'GM'),
                                                   ('sav', 'SAV')])
    categ_family_gruping = fields.Many2one('product.grouping.family', string='Grouping Family',
                                           compute='_compute_categ_family', inverse='_set_categ_family' , store=True, copy=True)
    product_obsolete = fields.Boolean(string='produit obsolète', compute='_compute_product_obsolete',
                                      inverse='_set_obsolete_product' ,store=True, copy=True)
    recall = fields.Boolean(string='Récylum', compute='_compute_recall', inverse='_set_recall' ,store=True, copy=True)
    margin_fixed = fields.Float(string='Marge Théorique fixe', compute='_compute_margin_fixed', inverse='_set_margin_fixed' ,store=True, copy=True)
    static = fields.Char(string='Stats N-1', compute='_compute_static', inverse='_set_static' ,store=True, copy=True)
    # specific fields for product template
    marge_product = fields.Float(string='Marge', compute='product_marge_compute')
    marge_product_percentage = fields.Float(string='Marge percentage', compute='product_marge_compute')
    marge_product_coef = fields.Float(string='Coef de marge', compute='product_marge_compute')
    impact_of_additional_cost = fields.Monetary(string="Impact of Additional Cost", compute='_compute_impact_of_additional_cost',
                                                inverse='_set_impact_of_additional_cost',store=True, copy=True)
    transportation = fields.Float(string="Transportation", compute='_compute_transportation', inverse='_set_transportation',store=True, copy=True)
    real_cost = fields.Float(string="Real Cost", compute="_get_real_cost")
    product_name = fields.Char(string='Libellé', compute='_compute_product_name', inverse='_set_product_name',
                               store=True)

    @api.depends('product_variant_ids', 'product_variant_ids.categ_family_gruping')
    def _compute_categ_family(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.categ_family_gruping = template.product_variant_ids.categ_family_gruping
        for template in (self - unique_variants):
            template.categ_family_gruping = False

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.product_name = self.name

    @api.depends('product_variant_ids', 'product_variant_ids.real_cost')
    def _compute_product_name(self):
        for record in self:
            if len(record.product_variant_ids) == 1:
                record.product_name = record.product_variant_ids.product_name
            else:
                record.product_name = False

    def _set_product_name(self):
        for record in self:
            if len(record.product_variant_ids) == 1:
                record.product_variant_ids.product_name = record.product_name

    def _set_categ_family(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.categ_family_gruping = template.categ_family_gruping

    @api.depends('product_variant_ids', 'product_variant_ids.product_obsolete')
    def _compute_product_obsolete(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.product_obsolete = template.product_variant_ids.product_obsolete
        for template in (self - unique_variants):
            template.product_obsolete = False

    def _set_obsolete_product(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.product_obsolete = template.product_obsolete

    def get_new_category(self):
        rec = self.env['product.template'].search([])
        for line in rec:
            if rec.product_family:
                family = self.env['product.family'].search([('id', '=', line.product_family.id)])
                category = self.env['product.category'].search([('name', '=', family.name)])
                if category:
                    line.categ_id = category

    @api.depends('product_variant_ids', 'product_variant_ids.recall')
    def _compute_recall(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.recall = template.product_variant_ids.recall
        for template in (self - unique_variants):
            template.recall = False

    def _set_recall(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.recall = template.recall

    @api.depends('product_variant_ids', 'product_variant_ids.margin_fixed')
    def _compute_margin_fixed(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.margin_fixed = template.product_variant_ids.margin_fixed
        for template in (self - unique_variants):
            template.margin_fixed = False

    def _set_margin_fixed(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.margin_fixed = template.margin_fixed

    @api.depends('product_variant_ids', 'product_variant_ids.static')
    def _compute_static(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.static = template.product_variant_ids.static
        for template in (self - unique_variants):
            template.static = False

    def _set_static(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.static = template.static

    @api.depends('product_variant_ids', 'product_variant_ids.transportation')
    def _compute_transportation(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.transportation = template.product_variant_ids.transportation
        for template in (self - unique_variants):
            template.transportation = False

    def _set_transportation(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.transportation = template.transportation

    @api.depends('product_variant_ids', 'product_variant_ids.impact_of_additional_cost')
    def _compute_impact_of_additional_cost(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.impact_of_additional_cost = template.product_variant_ids.impact_of_additional_cost
        for template in (self - unique_variants):
            template.impact_of_additional_cost = False

    def _set_impact_of_additional_cost(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.impact_of_additional_cost = template.impact_of_additional_cost

    @api.depends('product_variant_ids', 'product_variant_ids.marge_product')
    def product_marge_compute(self):
        for record in self:
            if len(record.product_variant_ids) == 1:
                record.marge_product = record.product_variant_ids.marge_product
                record.marge_product_percentage = record.product_variant_ids.marge_product_percentage
                record.marge_product_coef = record.product_variant_ids.marge_product_coef
            else:
                record.marge_product = False
                record.marge_product_percentage = False
                record.marge_product_coef = False

    @api.depends('product_variant_ids', 'product_variant_ids.real_cost')
    def _get_real_cost(self):
        for record in self:
            if len(record.product_variant_ids) == 1:
                record.real_cost = record.product_variant_ids.real_cost
            else:
                record.real_cost = False

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        for vals in vals_list:
            self._sanitize_vals(vals)
        templates = super(ProductTemplate, self).create(vals_list)
        if "create_product_product" not in self._context:
            templates._create_variant_ids()

        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('barcode'):
                related_vals['barcode'] = vals['barcode']
            if vals.get('default_code'):
                related_vals['default_code'] = vals['default_code']
            if vals.get('categ_family_gruping'):
                related_vals['categ_family_gruping'] = vals['categ_family_gruping']
            if vals.get('standard_price'):
                related_vals['standard_price'] = vals['standard_price']
            if vals.get('volume'):
                related_vals['volume'] = vals['volume']
            if vals.get('weight'):
                related_vals['weight'] = vals['weight']
            if vals.get('product_obsolete'):
                related_vals['product_obsolete'] = vals['product_obsolete']
            if vals.get('recall'):
                related_vals['recall'] = vals['recall']
            if vals.get('margin_fixed'):
                related_vals['margin_fixed'] = vals['margin_fixed']
            if vals.get('static'):
                related_vals['static'] = vals['static']
            if vals.get('transportation'):
                related_vals['transportation'] = vals['transportation']
            if vals.get('impact_of_additional_cost'):
                related_vals['impact_of_additional_cost'] = vals['impact_of_additional_cost']
            if vals.get('product_name'):
                related_vals['product_name'] = vals['product_name']
            # Please do forward port
            if related_vals:
                template.write(related_vals)

        return templates

    # add create method
    @api.model_create_multi
    def create(self, vals):
        if self.env.user.id != SUPERUSER_ID and not self.user_has_groups('salembier_sale.group_create_product'):
            raise UserError(_("You do not have the rights to create product."))
        else:
            return super(ProductTemplate, self).create(vals)

    # script to update product_name
    def get_the_name_of_product(self):
        product_template = self.env['product.template'].search([])
        for record in product_template:
            if record.name:
                record.product_name = record.name