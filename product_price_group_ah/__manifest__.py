{
    "name": "Cubes Hide Product Cost",
    "summary": "Hide Product Standard Price BY groups",
    'version': '17.0',
    'depends': ['product'],
    'author': "Ahmed Abdu,Cubes",

    'category': 'Product',
    'description': """
       Cubes - Hide Product Standard Price BY groups
    """,
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'views/product_template.xml',

    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
