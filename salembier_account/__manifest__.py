# -*- coding: utf-8 -*-
{
    'name': "salembier account",

    'summary': """
        customize account""",


    'author': "Sirius",
    'website': "http://www.sirius.com",

    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'stock', 'salambier_res_partner'],

    # always loaded
    'data': [
        'security/account_security.xml',
        'views/account_move.xml',
        'views/account_invoice_report.xml',
    ],

}