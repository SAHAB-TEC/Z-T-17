# -*- coding: utf-8 -*-
##############################################################################
#    Odoo, Open Source Management Solution
##############################################################################
{
    'name': 'Cubes Line Discount By Amount',
    'version': '1.1',
    'summary': 'Cubes Line Discount By Amount made by Abdulwahed Freaa 2023-01-01',
    'website': 'https://www.cubes.ly',
    'depends': ['base', 'account','sale','purchase'],

    'data': [
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/account_move.xml',
    ],

    'installable': True,
}
