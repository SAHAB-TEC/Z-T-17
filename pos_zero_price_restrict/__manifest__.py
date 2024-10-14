{
    'name': 'POS Restriction For Zero Price',
    'category': 'Point of Sale',
    'summary': 'This module will restrict zero price confirmation in POS.',
    'description': 'This module will help you to avoid zero price '
                   'confirmation in POS. It will show warning if zero '
                   'price confirmation occurred.',

    'depends': ['point_of_sale'],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'pos_zero_price_restrict/static/src/js/Screens'
    #         '/PaymentScreen/ProductScreen.js',
    #     ]
    # },
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_zero_price_restrict/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
