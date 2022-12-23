{
    'name': 'Import Product Packaging',
    'version': '15.0.0.1.0',
    'category': 'Stock',

    'author': 'Sirius-Info',
    'website': 'https://www.sirius-info.fr/',

    'summary': 'Import Product Packaging.',
    'description': """
This module used for Import Product Packaging.
==================================================
This module used for Import Product packaging.
       """,
    'depends': ['product','stock'],
    'data': [
        "security/ir.model.access.csv",
        'wizard/import_product_packaging_wiz_view.xml',
        'wizard/supplier_infoprice.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False
}
