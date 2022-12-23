# -*- coding: utf-8 -*-
{
    'name': 'Product Filter by Vendor Selection',
    "author": "Edge Technologies",
    'version': '15.0.1.0',
    'live_test_url': "https://youtu.be/by28iMEkjyw",
    "images":['static/description/main_screenshot.png'],
    'summary': "Product Filter by Vendors products filter by vendor product filter by supplier products filter by supplier selection product filter by supplier selection filter product by vendor filter product by supplier",
    'description': """ Product Filter by Vendor Selection.

    """,
    "license" : "OPL-1",
    'depends': ['base','purchase'],
    'data': [
        'security/filter_product_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'price': 6,
    'currency': "EUR",
    'category': 'Purchase',

}
