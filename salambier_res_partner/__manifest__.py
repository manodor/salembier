# -*- coding: utf-8 -*-
{
    'name': "Slambier res_partner",

    'summary': """
        amj module for change vendor and customer informations""",

    'description': """
        module for change vendor and customer
    """,

    'author': "Sirius",
    'website': "http://www.sirius.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'res partner',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','gts_partner_category'],

    # always loaded
    'data': [
        'security/partner_security.xml',
        'views/res_partner.xml',
        'views/account_fiscal_position.xml',
    ],
}
