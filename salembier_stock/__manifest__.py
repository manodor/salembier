# -*- coding: utf-8 -*-
{
    'name': "salembier stock",

    'summary': """
        customize stock""",


    'author': "Sirius",
    'website': "http://www.sirius.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','product', 'purchase', 'web'],

    # always loaded
    'data': [
        'report/deliveryslip_report.xml'
    ],

}
