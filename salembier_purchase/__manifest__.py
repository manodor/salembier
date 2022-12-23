# -*- coding: utf-8 -*-
{
    'name': "salembier Purchase",

    'summary': """
        customize Purchase""",

    'author': "Sirius",
    'website': "http://www.sirius.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'views/purchase_order_view.xml',
        'views/purchase_order_report.xml',
    ],

}
