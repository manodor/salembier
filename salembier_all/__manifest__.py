# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright © 2020,Weasydoo. All rights reserved.
##############################################################################
{
    'name': "Salembier ERP",
    'description': """
        Odoo aplication for Salembier""",
    'author': 'sirius',
    'website': "http://sirius.com",
    'category': 'Distribution',
    'version': '15.0.1.0.0',
    'depends': [
            'sale',
            'purchase',
            'stock',
            'account',
            'mrp',
            'calendar',
            'contacts',
            'repair',
            'sale_renting',
            'salembier_sale',
            'salembier_purchase',
            'salambier_res_partner',
            'salembier_account',
            'salembier_stock',
            'sale_discount_total',
            'reorder_rule_import',
            'purchase_order_line_default_packaging',
            'product_filter_by_vendor',
            'partner_fax',
            'mass_editing',
            'ksc_purchase_intelligence',
            'ksc_import_product_variants',
            'iwesabe_product_image_so_line',
            'gts_partner_category',
            'base_partner_sequence_salembier',
            'sale_order_line_default_packaging',

    ],
    'data': [
    ],
    'application': True,
}
