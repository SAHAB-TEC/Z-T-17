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
    'version': '16.0',
    'depends': ['base', 'product'],
    "data": [
        "views/product_category_views.xml",
        "security/ir.model.access.csv",
        'security/ir_rule.xml'
    ],
    'license': 'OPL-1',
    "pre_init_hook": None,
    "post_init_hook": None,
}