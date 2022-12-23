# -*- coding: utf-8 -*-
{
    'name': "salembier sale",

    'summary': """
        customize sale""",


    'author': "Sirius",
    'website': "http://www.sirius.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','product', 'purchase', 'web'],

    # always loaded
    'data': [
        'data/cron.xml',
        'security/ir.model.access.csv',
        'security/product_security.xml',
        'report/sale_order_report.xml',
        'views/sale_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/stock_move_line_view.xml',
        'views/purchase_order_view.xml',
        'views/product_grouping_family_view.xml',
        'views/product_category_view.xml',
        'views/product_pricelist_view.xml',
    ],

}
