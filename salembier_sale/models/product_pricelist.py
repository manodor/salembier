from itertools import chain

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids, grp_family_ids):
        self.ensure_one()
        # Load all rules
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id', 'active'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            LEFT JOIN product_grouping_family AS grp_family ON item.grouping_family_id = grp_family.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.grouping_family_id IS NULL OR item.grouping_family_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
                AND (item.active = TRUE)
            ORDER BY
                item.grouping_family_id ,item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, prod_ids, categ_ids, grp_family_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Datetime.now()
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}
        categ_ids = {}
        grp_family_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
            grp_family = p.categ_family_gruping
            while grp_family:
                grp_family_ids[grp_family.id] = True
                grp_family = None
        categ_ids = list(categ_ids)
        grp_family_ids = list(grp_family_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids,
                                                   categ_ids, grp_family_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty,
                                                                                                              product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['uom.uom'].browse([qty_uom_id])
            for rule in items:
                if not rule._is_applicable_for(product, qty_in_product_uom):
                    continue
                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.company, date, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                if price is not False:
                    # pass the date through the context for further currency conversions
                    rule_with_date_context = rule.with_context(date=date)
                    price = rule_with_date_context._compute_price(price, price_uom, product, quantity=qty, partner=partner)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    cur = product.cost_currency_id
                else:
                    cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
        return results


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    grouping_family_id = fields.Many2one('product.grouping.family', 'Product Grouping Family')
    applied_on = fields.Selection([
        ('4_grouping_family', 'Grouping Family'),
        ('3_global', 'All Products'),
        ('2_product_category', 'Product Category'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='3_global', required=True,
        help='Pricelist Item applicable on selected option')
    # applied_on = fields.Selection(selection_add=[('4_grouping_family', 'Grouping Family'), ('3_global',),], ondelete='set null')

    @api.constrains('product_id', 'product_tmpl_id', 'categ_id')
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "2_product_category" and not item.categ_id:
                raise ValidationError(_("Please specify the category for which this rule should be applied"))
            elif item.applied_on == "4_grouping_family" and not item.grouping_family_id:
                raise ValidationError(_("Please specify the Grouping Family for which this rule should be applied"))
            elif item.applied_on == "1_product" and not item.product_tmpl_id:
                raise ValidationError(_("Please specify the product for which this rule should be applied"))
            elif item.applied_on == "0_product_variant" and not item.product_id:
                raise ValidationError(_("Please specify the product variant for which this rule should be applied"))

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.grouping_family_id and item.applied_on == '4_grouping_family':
                item.name = _("Grouping family: %s") % (item.grouping_family_id.name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s") % (item.product_id.with_context(display_default_code=False).display_name)
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                item.price = formatLang(item.env, item.fixed_price, monetary=True, dp="Product Price",
                                        currency_obj=item.currency_id)
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount", item.percent_price)
            else:
                item.price = _("%(percentage)s %% discount and %(price)s surcharge", percentage=item.price_discount,
                               price=item.price_surcharge)

    @api.onchange('product_id', 'product_tmpl_id', 'categ_id', 'grouping_family_id')
    def _onchane_rule_content(self):
        if not self.user_has_groups('product.group_sale_pricelist') and not self.env.context.get('default_applied_on',
                                                                                                 False):
            # If advanced pricelists are disabled (applied_on field is not visible)
            # AND we aren't coming from a specific product template/variant.
            variants_rules = self.filtered('product_id')
            template_rules = (self - variants_rules).filtered('product_tmpl_id')
            variants_rules.update({'applied_on': '0_product_variant'})
            template_rules.update({'applied_on': '1_product'})
            (self - variants_rules - template_rules).update({'applied_on': '3_global'})

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('applied_on', False):
                # Ensure item consistency for later searches.
                applied_on = values['applied_on']
                if applied_on == '3_global':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, grouping_family_id=None))
                elif applied_on == '4_grouping_family':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
                elif applied_on == '2_product_category':
                    values.update(dict(product_id=None, product_tmpl_id=None))
                elif applied_on == '1_product':
                    values.update(dict(product_id=None, categ_id=None))
                elif applied_on == '0_product_variant':
                    values.update(dict(categ_id=None))
        return super(PricelistItem, self).create(vals_list)

    def write(self, values):
        if values.get('applied_on', False):
            # Ensure item consistency for later searches.
            applied_on = values['applied_on']
            if applied_on == '3_global':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, grouping_family_id=None))
            elif applied_on == '4_grouping_family':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '2_product_category':
                values.update(dict(product_id=None, product_tmpl_id=None))
            elif applied_on == '1_product':
                values.update(dict(product_id=None, categ_id=None))
            elif applied_on == '0_product_variant':
                values.update(dict(categ_id=None))
        res = super(PricelistItem, self).write(values)
        # When the pricelist changes we need the product.template price
        # to be invalided and recomputed.
        self.env['product.template'].invalidate_cache(['price'])
        self.env['product.product'].invalidate_cache(['price'])
        return res

    def _is_applicable_for(self, product, qty_in_product_uom):
        """Check whether the current rule is valid for the given product & qty.
        Note: self.ensure_one()
        :param product: product record (product.product/product.template)
        :param float qty_in_product_uom: quantity, expressed in product UoM
        :returns: Whether rules is valid or not
        :rtype: bool
        """
        self.ensure_one()
        product.ensure_one()
        res = True

        is_product_template = product._name == 'product.template'
        if self.min_quantity and qty_in_product_uom < self.min_quantity:
            res = False

        elif self.categ_id:
            # Applied on a specific category
            cat = product.categ_id
            while cat:
                if cat.id == self.categ_id.id:
                    break
                cat = cat.parent_id
            if not cat:
                res = False
        elif self.grouping_family_id:
            # Applied on a specific Grouping Family
            grp_family = product.categ_family_gruping
            # while grp_family:
            #     if grp_family.id == self.grouping_family_id.id:
            #         break
            #     grp_family = grp_family.parent_id
            if not grp_family:
                res = False
        else:
            # Applied on a specific product template/variant
            if is_product_template:
                if self.product_tmpl_id and product.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and not (
                    product.product_variant_count == 1
                    and product.product_variant_id.id == self.product_id.id
                ):
                    # product self acceptable on template if has only one variant
                    res = False
            else:
                if self.product_tmpl_id and product.product_tmpl_id.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and product.id != self.product_id.id:
                    res = False

        return res
