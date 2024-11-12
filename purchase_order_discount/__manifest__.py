# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Discount',  
      'summary': 'Add discount amount to purchase order lines and adjust total',    'category': 'Purchases',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_view.xml',
        'views/account_move_view.xml'
    ],
    'installable': True,
    'application': False,
    
}
