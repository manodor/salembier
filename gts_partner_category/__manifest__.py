
{
    'name': '''Partner Category | Partners Hierarchy''',
    'summary': 'This module is used to categorize the partner' ,
    'description': """
        Assign categories to customer
        Assign categories to vendor 
        Assign categories to supplier
        customer category vendor category supplier category
        Partner Hierarchy vendor Hierarchy supplier Hierarchy
        partner By Category
        Customer/Vendor By Category Customer By Category Vendor By Category
        Partner By Category, Category of Partner, partner by category, category of partner,  
        partnerbycategory, categoryofpartner, partner-category, category-partner,  
        partner_category, category_partner,  
        Customer/Vendor By Category Customer By Category Vendor By Category
        Partner Category, PartnerCategory, partner category, partner category,
        Partners Hierarchy, PartnersHierarchy,  partners hierarchy,  partnershierarchy,
        category customer, customer category, category_customer, customer_category,
        Category-Customer, customer-category, Category_Customer, Customer_Category,
        Category of Customer, customer categories, assign Category of Customer, Customer_Categories,
        Categories of Customer, assign customer categories, assign Customer_Categories,
        category vendor, vendor category, category_vendor, vendor_category,
        Category-Vendor, vendor-category, Category_Vendor, Vendor_Category,
        Category of Vendor, customer categories, assign Category of Vendor, Vendor_Categories,
        Categories of Vendor, assign Vendor categories, assign Vendor_Categories,
        category supplier, supplier category, category_supplier, supplier_category,
        Category-Supplier, supplier-category, Category_Supplier, Supplier_Category,
        Category of Supplier, customer categories, assign Category of Supplier, Supplier_Categories,
        Categories of Supplier, assign Supplier categories, assign Supplier_Categories,
        PARTNER BY CATEGORY, CATEGORY OF PARTNER, PARTNER BY CATEGORY, CATEGORY OF PARTNER,  
        PARTNERBYCATEGORY, CATEGORYOFPARTNER, PARTNER-CATEGORY, CATEGORY-PARTNER,  
        PARTNER_CATEGORY, CATEGORY_PARTNER,  
        CUSTOMER/VENDOR BY CATEGORY CUSTOMER BY CATEGORY VENDOR BY CATEGORY
        PARTNER CATEGORY, PARTNERCATEGORY, PARTNER CATEGORY, PARTNER CATEGORY,
        PARTNERS HIERARCHY, PARTNERSHIERARCHY,  PARTNERS HIERARCHY,  PARTNERSHIERARCHY,
        CATEGORY CUSTOMER, CUSTOMER CATEGORY, CATEGORY_CUSTOMER, CUSTOMER_CATEGORY,
        CATEGORY-CUSTOMER, CUSTOMER-CATEGORY, CATEGORY_CUSTOMER, CUSTOMER_CATEGORY,
        CATEGORY OF CUSTOMER, CUSTOMER CATEGORIES, ASSIGN CATEGORY OF CUSTOMER, CUSTOMER_CATEGORIES,
        CATEGORIES OF CUSTOMER, ASSIGN CUSTOMER CATEGORIES, ASSIGN CUSTOMER_CATEGORIES,
        CATEGORY VENDOR, VENDOR CATEGORY, CATEGORY_VENDOR, VENDOR_CATEGORY,
        CATEGORY-VENDOR, VENDOR-CATEGORY, CATEGORY_VENDOR, VENDOR_CATEGORY,
        CATEGORY OF VENDOR, CUSTOMER CATEGORIES, ASSIGN CATEGORY OF VENDOR, VENDOR_CATEGORIES,
        CATEGORIES OF VENDOR, ASSIGN VENDOR CATEGORIES, ASSIGN VENDOR_CATEGORIES,
        CATEGORY SUPPLIER, SUPPLIER CATEGORY, CATEGORY_SUPPLIER, SUPPLIER_CATEGORY,
        CATEGORY-SUPPLIER, SUPPLIER-CATEGORY, CATEGORY_SUPPLIER, SUPPLIER_CATEGORY,
        CATEGORY OF SUPPLIER, CUSTOMER CATEGORIES, ASSIGN CATEGORY OF SUPPLIER, SUPPLIER_CATEGORIES,
        CATEGORIES OF SUPPLIER, ASSIGN SUPPLIER CATEGORIES, ASSIGN SUPPLIER_CATEGORIES
    """,
    'category': 'Extra Tools',
    'version': '14.0.0.1',
    'sequence': 1,
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/partner_category_view.xml',
    ],
    'license': 'OPL-1',
    "images": ["static/description/banner.png"],
    'price': '0.00',
    'currency': "EUR",
    'installable': True,
    'application': True,
}
