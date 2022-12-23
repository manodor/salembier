# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': ' Import Reordering Rule from Excel or CSV file in odoo',
    'version': '15.0.0.2',
    'category': 'Stock',
    'summary': 'Data import app for import Reordering rules import Minimum order rules import Minimum stock rule Import stock rules from Excel import reorder rule from excel import stock min and max rules import product stock rules import product reordering rules import',
    'description': """
            This Module will provide a feature where you can update or create minimum and maximum stock rule for products by just adding a CSV file.
    Minimum stock rule import, minimum product stock import, mininum order rule import, Reordering rule import from CSV,Reordering rule import from Excel.
     odoo reorder rule import
     odoo import reorder rules from csv in odoo import minimun stock rule from excel
     odoo import reorderrule import from csv import minimum stockrule import odoo import minimum order rule import
     odoo import minimum orderrule import odoo Import Reordering Rules from CSV/Excel file
    odoo Import stock with Serial number import
    odoo Import stock with lot number import
    odoo import lot number with stock import
    odoo import serial number with stock import
    odoo import lines import
    odoo import order lines import
    odoo import orders lines import
    import so lines import
    imporr po lines import
    import invoice lines import
    import invoice line import


Este Módulo proporcionará una función en la que puede actualizar o crear una regla de existencias mínima y máxima para productos simplemente agregando un archivo CSV.
     Importación de regla de stock mínima, importación mínima de stock de producto, importación de regla de orden mínima, importación de regla de reordenación desde CSV, importación de regla de reordenación desde Excel.

ستوفر لك هذه الوحدة ميزة يمكنك من خلالها تحديث أو إنشاء قاعدة المخزون الأدنى والحد الأدنى للمنتجات عن طريق إضافة ملف CSV فقط.
     الحد الأدنى من استيراد قواعد المخزون ، استيراد الحد الأدنى من مخزون المنتجات ، استيراد قاعدة الطلبية ، إعادة استيراد القاعدة من CSV ، إعادة استيراد القاعدة من Excel.

Ce module fournira une fonctionnalité où vous pouvez mettre à jour ou créer une règle de stock minimum et maximum pour les produits en ajoutant simplement un fichier CSV.
     Importation de règle de stock minimum, importation de stock de produit minimum, importation de règle de commande mininum, importation de règle de réorganisation à partir de CSV, importation de règle de réorganisation à partir d'Excel.

Este Módulo fornecerá um recurso onde você pode atualizar ou criar a regra de estoque mínima e máxima para os produtos apenas adicionando um arquivo CSV.
     Importação de regra mínima de estoque, importação mínima de estoque de produto, importação de regra de ordem mínima, Regra de regra importada de CSV, Regra de regra de importação de Excel.
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'price': 10,
    'license': 'OPL-1',
    'currency': "EUR",
    'depends': ['base', 'stock','sale_management'],
    'data': [
        'security/ir.model.access.csv',  
        'wizard/wizard_import_view.xml',
        'data/attachment_sample.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url':'https://youtu.be/uyOAgeuAmFE',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
