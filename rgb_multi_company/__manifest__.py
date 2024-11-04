# -*- coding: utf-8 -*-
{
    'name': "Multi Company Edits",
    'summary': """
        summary
    """,
    'description': """
        description
    """,
    'author': "Ragab",
    'contributors': [
        'Ragab Deaf <ragabdeaf93@outlook.com>',
    ],
    'version': '17.0',
    'depends': ['base', 'product', 'point_of_sale'],
    "data": [
        "views/product_category_views.xml",
        "security/ir.model.access.csv",
        'security/ir_rule.xml',
        'views/partner.xml',
        'data/sequence.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'rgb_multi_company/static/src/**/*'
        ],
    },
    'license': 'OPL-1',
    "pre_init_hook": None,
    "post_init_hook": None,
}