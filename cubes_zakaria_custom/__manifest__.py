{
    'name': "Cubes Zakaria Custom",
    'version': '1.0',
    'depends': ['base','sale','purchase','stock_account'],
    'author': "Cubes Zakaria Custom",

    'category': 'Category',
    'description': """
    Cubes Zakaria Custom Module made by Abdalwahed 2022-10-26
    """,
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'view/sale_order_edited_view.xml',
        'view/purchase_order_edited_view.xml',
        'view/stock_valuation_layer.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
