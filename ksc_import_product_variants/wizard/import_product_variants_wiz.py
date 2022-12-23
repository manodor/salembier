from odoo import models, fields, api, _
import binascii
import tempfile
import xlrd
import base64

import logging

logger = logging.getLogger(__name__)


class ImportProductVariants(models.TransientModel):
    _name = 'import.product.variant'

    import_file = fields.Binary("Import File")

    def import_product_variants(self):
        text_to_import = base64.decodebytes(self.import_file)
        workbook = xlrd.open_workbook(file_contents=text_to_import)
        sheet = workbook.sheet_by_index(0)
        old_product = False
        first_product = self.env['product.product']
        first_price = 0.0
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
            else:
                raw_values = list(
                    map(lambda row: isinstance(row.value, str) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))
                if isinstance(raw_values[0], bytes):
                    product_code = raw_values[0].decode("utf-8")
                else:
                    product_code = str(raw_values[0]).strip()

                if isinstance(raw_values[15], bytes):
                    description_sale = raw_values[15].decode("utf-8")
                else:
                    description_sale = str(raw_values[15]).strip()

                if isinstance(raw_values[1], bytes):
                    product_name_origin = raw_values[1].decode("utf-8")
                else:
                    product_name_origin = str(raw_values[1]).strip()

                if isinstance(raw_values[4], bytes):
                    code = raw_values[4].decode("utf-8")
                else:
                    code = str(raw_values[4]).strip()

                if isinstance(raw_values[5], bytes):
                    name = raw_values[5].decode("utf-8")
                else:
                    name = str(raw_values[5]).strip()

                if isinstance(raw_values[43], bytes):
                    margin_fixed = raw_values[43].decode("utf-8")
                else:
                    margin_fixed = str(raw_values[43]).strip()

                if isinstance(raw_values[42], bytes):
                    recall = raw_values[42].decode("utf-8")
                    if recall == 'Non':
                        recall = False
                    else:
                        recall = True
                else:
                    recall = str(raw_values[42]).strip()
                    if recall == 'Non':
                        recall = False
                    else:
                        recall = True

                if isinstance(raw_values[47], bytes):
                    marge_product = raw_values[47].decode("utf-8")
                else:
                    marge_product = str(raw_values[47]).strip()

                if isinstance(raw_values[36], bytes):
                    transportation = raw_values[36].decode("utf-8")
                else:
                    transportation = str(raw_values[36]).strip()

                if isinstance(raw_values[35], bytes):
                    impact_of_additional_cost = raw_values[35].decode("utf-8")
                else:
                    impact_of_additional_cost = str(raw_values[35]).strip()

                if isinstance(raw_values[37], bytes):
                    real_cost = raw_values[37].decode("utf-8")
                else:
                    real_cost = str(raw_values[37]).strip()

                # Add supplier line
                supplier = {}
                if isinstance(raw_values[19], bytes):
                    supplier_name = raw_values[19].decode("utf-8")
                    # delete the .0 from the string supplier_name
                    supplier_name = supplier_name.replace('.0', '')
                    supplier_id = self.env['res.partner'].search([('ref', 'like', supplier_name)],
                                                                 limit=1)
                    purchase_price = raw_values[33]
                    currency = raw_values[31]
                    currency_id = self.env['res.currency'].search([('name', '=ilike', currency)],
                                                                  limit=1)
                    if currency_id:
                        currency_id = currency_id.id
                    else:
                        currency_id = 1
                    product_name_supplier = raw_values[50]
                    product_code_supplier = raw_values[49]
                else:
                    supplier_name = str(raw_values[19]).strip()
                    supplier_name = supplier_name.replace('.0', '')
                    supplier_id = self.env['res.partner'].search([('ref', 'like', supplier_name)],
                                                                 limit=1)
                    purchase_price = raw_values[33]
                    currency = str(raw_values[31]).strip()
                    currency_id = self.env['res.currency'].search([('name', '=ilike', currency)],
                                                                  limit=1)
                    if currency_id:
                        currency_id = currency_id.id
                    else:
                        currency_id = 1
                    product_name_supplier = str(raw_values[50]).strip()
                    product_name_supplier = product_name_supplier.replace("b'", '')
                    product_code_supplier = str(raw_values[49]).strip()
                    product_code_supplier = product_code_supplier.replace("b'", '')

                # add static fields
                if isinstance(raw_values[44], bytes):
                    static = raw_values[44].decode("utf-8")
                else:
                    static = raw_values[44].strip()

                # add obsolete fields
                if isinstance(raw_values[25], bytes):
                    if raw_values[25].decode("utf-8") == 'Non':
                        obsolete = False
                    else:
                        obsolete = True
                else:
                    obsolete = raw_values[25].strip()
                    if obsolete == 'Non':
                        obsolete = False
                    else:
                        obsolete = True

                # add standard_price fields
                if isinstance(raw_values[30], bytes):
                    standard_price = raw_values[30].decode("utf-8")
                else:
                    standard_price = raw_values[30].strip()

                # add sale_price fields
                if isinstance(raw_values[51], bytes):
                    sale_price = raw_values[51].decode("utf-8")
                else:
                    sale_price = raw_values[51].strip()

                # add categ grouping fields
                if isinstance(raw_values[29], bytes):
                    categ_grouping_code = raw_values[29].decode("utf-8")
                    value = self.env['product.grouping.family'].search([('name', '=ilike', categ_grouping_code)],
                                                                       limit=1)
                    if value:
                        categ_grouping = value
                    else:
                        categ_grouping = None
                else:
                    categ_grouping_code = raw_values[29].strip()
                    value = self.env['product.grouping.family'].search([('name', '=ilike', categ_grouping_code)],
                                                                       limit=1)
                    if value:
                        categ_grouping = value
                    else:
                        categ_grouping = None

                # add package sale
                if isinstance(raw_values[27], bytes):
                    package_name = raw_values[27].decode("utf-8")
                    package_sale = False
                    qty = raw_values[27].decode("utf-8")
                else:
                    package_name = raw_values[27].strip()
                    package_sale = False
                    qty = raw_values[27].strip()
                # add package purchase
                if isinstance(raw_values[26], bytes):
                    package_purchase_name = raw_values[26].decode("utf-8")
                    package_purchase = False
                    qty_packaging_purchase = raw_values[26].decode("utf-8")
                else:
                    package_purchase_name = raw_values[26].strip()
                    package_purchase = False
                    qty_packaging_purchase = raw_values[26].strip()

                product = self.env['product.template'].search(['|', ('default_code', '=', code),
                                                               ('name', '=', name)], limit=1)
                if not product:
                    product = self.env['product.template'].search([('name', '=', name), ('active', '=', False)],
                                                                  limit=1)
                if old_product == product.id:
                    count = 1
                else:
                    count = 0
                    old_product = product.id
                line_id = self.env['product.template.attribute.line']
                value_id = self.env['product.attribute.value']

                if isinstance(raw_values[7], bytes):
                    taille = raw_values[7].decode("utf-8")
                else:
                    taille = str(raw_values[7]).strip()
                if taille:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Taille')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == taille)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': taille,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})

                if isinstance(raw_values[8], bytes):
                    contenance = raw_values[8].decode("utf-8")
                else:
                    contenance = str(raw_values[8]).strip()
                if contenance:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Contenance')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == contenance)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': contenance,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})

                if isinstance(raw_values[9], bytes):
                    durete = raw_values[9].decode("utf-8")
                else:
                    durete = str(raw_values[9]).strip()
                if durete:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Dureté')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == durete)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': durete,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})

                if isinstance(raw_values[10], bytes):
                    epaisseur = raw_values[10].decode("utf-8")
                else:
                    epaisseur = str(raw_values[10]).strip()
                if epaisseur:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Epaisseur')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == epaisseur)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': epaisseur,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})

                if isinstance(raw_values[11], bytes):
                    couleur = raw_values[11].decode("utf-8")
                else:
                    couleur = str(raw_values[11]).strip()
                if couleur:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Couleur')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == couleur)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': couleur,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})
                if isinstance(raw_values[12], bytes):
                    grain = raw_values[12].decode("utf-8")
                else:
                    grain = str(raw_values[12]).strip()
                if grain:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Grain')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == grain)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': grain,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})
                if isinstance(raw_values[13], bytes):
                    finition = raw_values[13].decode("utf-8")
                else:
                    finition = str(raw_values[13]).strip()
                if finition:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Finition')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == finition)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': finition,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})
                if isinstance(raw_values[14], bytes):
                    format = raw_values[14].decode("utf-8")
                else:
                    format = str(raw_values[14]).strip()
                if isinstance(raw_values[51], bytes):
                    product_price = raw_values[51].decode("utf-8")
                else:
                    product_price = str(raw_values[51]).strip()
                if format:
                    attribute = self.env['product.attribute'].search([('name', '=', 'Format')], limit=1)
                    value = attribute.value_ids.filtered(lambda r: r.name == format)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': format,
                                                                            'attribute_id': attribute.id})
                    value_id |= value
                    attribute_line = product.attribute_line_ids.filtered(lambda r: r.attribute_id == attribute)
                    if attribute_line:
                        line_id |= attribute_line
                        line_value = product.attribute_line_ids.filtered(
                            lambda r: r.attribute_id == attribute).mapped('value_ids')
                        if value not in line_value:
                            attribute_line.value_ids = [(4, value.id)]
                    else:
                        line_id |= self.env['product.template.attribute.line'].create({'attribute_id': attribute.id,
                                                                                       'value_ids': [(4, value.id)],
                                                                                       'product_tmpl_id': product.id})
                #  Search Product and Update the Internal REF
                attribute_value_ids = self.env['product.template.attribute.value'].search([
                    ('product_tmpl_id', '=', product.id),
                    ('attribute_line_id', 'in', line_id.ids),
                    ('product_attribute_value_id', 'in', value_id.ids)])
                self.env.cr.commit()
                if count == 0:
                    product_id = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                    if len(product_id) == 1:
                        first_product = product_id
                        first_price = product_price
                        product_id['default_code'] = product_code
                        product_id['product_name'] = product_name_origin
                        product_id['description_sale'] = description_sale
                        product_id['margin_fixed'] = margin_fixed
                        product_id['recall'] = recall
                        product_id['real_cost'] = real_cost
                        product_id['marge_product'] = marge_product
                        product_id['transportation'] = transportation
                        product_id['impact_of_additional_cost'] = impact_of_additional_cost
                        product_id['static'] = static
                        product_id['product_obsolete'] = obsolete
                        product_id['lst_price'] = sale_price
                        product_id['standard_price'] = standard_price
                        if categ_grouping:
                            p['categ_family_gruping'] = categ_grouping
                        if supplier_id:
                            product_id['variant_seller_ids'] = [(0, 0, {'name': supplier_id.id,
                                                                        'price': purchase_price,
                                                                        'currency_id': currency_id,
                                                                        'product_name': product_name_supplier,
                                                                        'product_code': product_code_supplier,
                                                                        'current_vendor': True,
                                                                        'product_uom': product_id.uom_id.id,
                                                                        'product_id': product_id.id,
                                                                        })]
                        if package_name and float(qty) > 0:
                            product_id['packaging_ids'] = [(0, 0, {'name': product.name,
                                                                   'sales': package_sale,
                                                                   'qty': float(qty),
                                                                   'product_uom_id': product_id.uom_id.id,
                                                                   })]
                        # self.env.cr.commit()
                        product_id.product_tmpl_id.list_price = 0.0
                product_id = self.env['product.product'].search(
                    [('product_template_variant_value_ids', 'in', attribute_value_ids.ids)])
                for p in product_id:
                    if p.product_template_variant_value_ids in attribute_value_ids or p.product_template_variant_value_ids == attribute_value_ids:
                        if first_product.product_template_variant_value_ids:
                            first_product.product_template_variant_value_ids[0].price_extra = first_price
                            first_product.product_tmpl_id.list_price = 0.0
                        if p.product_template_variant_value_ids:
                            p.product_template_variant_value_ids[0].price_extra = product_price
                        p['default_code'] = product_code
                        p['product_name'] = product_name_origin
                        p['description_sale'] = description_sale
                        p['margin_fixed'] = margin_fixed
                        p['recall'] = recall
                        p['real_cost'] = real_cost
                        p['marge_product'] = marge_product
                        p['transportation'] = transportation
                        p['impact_of_additional_cost'] = impact_of_additional_cost
                        p['static'] = static
                        p['product_obsolete'] = obsolete
                        p['lst_price'] = sale_price
                        p['standard_price'] = standard_price
                        if categ_grouping:
                            p['categ_family_gruping'] = categ_grouping
                        if supplier_id.id:
                            p['variant_seller_ids'] = [(0, 0, {'name': supplier_id.id,
                                                               'price': purchase_price,
                                                               'currency_id': currency_id,
                                                               'product_name': product_name_supplier,
                                                               'product_code': product_code_supplier,
                                                               'current_vendor': True,
                                                               'product_uom': product_id.uom_id.id,
                                                               'product_id': p.id,
                                                               })]
                        if float(package_name) > 0:
                            p['packaging_ids'] = [(0, 0, {'name': p.name,
                                                          'purchase': package_sale,
                                                          'qty': float(package_name),
                                                          'product_uom_id': p.uom_id.id,
                                                          })]
                        if float(package_purchase_name) > 0:
                            p['packaging_ids'] = [(0, 0, {'name': p.name,
                                                          'sales': package_purchase,
                                                          'qty': float(package_purchase_name),
                                                          'product_uom_id': p.uom_id.id,
                                                          })]
                        # self.env.cr.commit()
                        p.product_tmpl_id.list_price = 0.0
        return {}
