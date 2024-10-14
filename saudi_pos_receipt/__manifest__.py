# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Saudi Point of Sale Receipt",
    "author": "Mohamed Saber",
    "category": "Accounting/Localizations/Point of Sale",
    "description": """
        Saudi Point of Sale Receipt
    """,
    "depends": ["point_of_sale", "l10n_gcc_pos"],
    "data": [
        "views/pos_order_view.xml",
        "views/pos_config_view.xml",
    ],
    # 'assets': {
    #     'web.assets_qweb': [
    #         'saudi_pos_receipt/static/src/xml/OrderReceipt.xml',
    #     ],
    #     'point_of_sale.assets': [
    #         'saudi_pos_receipt/static/src/css/pos_receipts.css',
    #     ]
    # },
    
    # "assets": {
    #     "point_of_sale._assets_pos": [
    #         "saudi_pos_receipt/static/src/**/*",
    #     ],
    #     # "web.assets_frontend": [
    #     #     "saudi_pos_receipt/static/src/css/pos_receipts.css",
    #     # ],
    # },
}
