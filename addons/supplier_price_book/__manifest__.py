{
    'name': 'Справочник цен поставщиков',
    'version': '19.0.4.0.0',
    'summary': 'Закупки: цены (US3), график (US4), дефицит (US1), возврат (US5)',
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
