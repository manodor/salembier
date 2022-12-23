# -*- coding: utf-8 -*-
{
    'name': "salembier photos import",

    'summary': """
        Import photos products from internal reference name""",


    'author': "Sirius",
    'website': "http://www.sirius.com",

    'category': 'product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'datas/cron.xml'
    ],

}