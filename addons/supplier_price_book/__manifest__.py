{
    'name': 'Справочник цен поставщиков',
    'version': '19.0.3.0.0',
    'summary': 'Закупки: цены поставщиков (US3), график поставки (US4), дефицит сырья (US1)',
    'category': 'Purchase',
    'depends': ['purchase', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/raw_material_shortage_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
