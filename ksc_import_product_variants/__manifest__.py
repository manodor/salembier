{
    'name': 'KSC Import Product Variants',
    'version': '15.0.0.1.0',
    'category': 'Account',

    'author': 'Konsultoo Software Consulting PVT. LTD.',
    'maintainer': 'Konsultoo Software Consulting PVT. LTD.',
    'contributors': ["Konsultoo Software Consulting PVT. LTD."],
    'website': 'https://www.konsultoo.com/',

    'summary': 'Import Product Variants.',
    'description': """
This module used for Import Product Variants.
==================================================
This module used for Import Product Variants.
       """,
    'depends': ['product', 'salembier_sale'],
    'data': [
        "security/ir.model.access.csv",
        'wizard/import_product_variants_wiz_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False
}
