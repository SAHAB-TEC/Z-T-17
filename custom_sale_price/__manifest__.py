{
    'name': "Custom Sale price",
    'version': '1.0',
    'depends': ['sale'],
    'author': "Cubes Zakaria Custom",

    'category': 'Category',
    'description': """
       Custom module for add sale price gros in report sale
    """,
    # data files always loaded at installation
    'data': [
        'views/sale_order_view.xml',
        'report/report_saleorder_document.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
