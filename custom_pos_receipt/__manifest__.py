# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'POS Custom Receipt',
    'category': 'Sales/Point of Sale',
    'summary': 'This module is used to customized receipt of point of sale when a user adds a product in the cart and validates payment and print receipt, then the user can see the client name on POS Receipt. | Custom Receipt | POS Reciept | Payment | POS Custom Receipt',
    'description': "Customized our point of sale receipt",
    'version': '17.0',
    'website': 'https://www.kanakinfosystems.com',
    'author': 'Kanak Infosystems LLP.',
    'images': ['static/description/banner.jpg'],
    'depends': ['base', 'point_of_sale'],
    # 'assets': {
    #     'web.assets_qweb': [
    #         "custom_pos_receipt/static/src/xml/pos.xml",
    #     ],
    # },
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_pos_receipt/static/src/**/*',
        ],
    },
    'installable': True,
    'license': 'AGPL-3',

}
