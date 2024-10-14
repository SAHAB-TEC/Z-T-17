{
    'name': 'Cubes Product Template Export',
    'summary': """Cubes Product Template Export.""",
    'description': """
       Only product export group can export product template.
    """,
    'depends': ['base_setup', 'mail','product','web'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
    ],
    # 'assets': {
    #     'web.assets_qweb': [
    #         'cubes_product_template_export/static/src/xml/import_cmd.xml',
    #     ],
    #     'web.assets_backend': [
    #         'cubes_product_template_export/static/src/js/list_controller.js',
    #         'cubes_product_template_export/static/src/js/kanban_controller.js'
    #     ]
    # },
    'assets': {
        'web.assets_backend': [
            'cubes_product_template_export/static/src/components/**/*',
            'cubes_product_template_export/static/src/**/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
