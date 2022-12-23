{
    "name": "Purchase Intelligence",
    "summary": "Generate a Purchase Intelligence data.",
    "version": "15.0.0.1.0",

    'author':'Konsultoo Software Consulting PVT. LTD.',
    'maintainer': 'Konsultoo Software Consulting PVT. LTD.',
    'contributors': ["Konsultoo Software Consulting PVT. LTD."],
    'website': 'https://www.konsultoo.com/',
    "category": "Purchase",

    "depends": ['purchase', 'stock', 'salembier_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_intelligence_view.xml',
        'views/stock_warehouse_orderpoint_view.xml',
        'wizard/confirm_box_view.xml',
        'wizard/add_intelligence_line_view.xml',
    ],

    "auto_install": False,
    "application": True,
    "installable": True,
}

