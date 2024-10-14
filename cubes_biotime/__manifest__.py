# -*- coding: utf-8 -*-
{
    'name': "Cubes Biotime Integration",

    'summary': "Cubes Biotime Integration",

    'description': """
        Cubes Biotime Integration
    """,

    'author': 'Cubes Technology',
    'website': 'http://www.cubes.ly/',
    'category': 'Hr',
    'version': '0.1',
    'depends': ['base', 'hr', 'hr_attendance'],
    'external_dependencies': {
        'python': [
            'pyzk',
            'openpyxl',
        ],
    },
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/biotime.xml',
        'views/terminal.xml',
        'views/employee.xml',
        'data/menuitems.xml',
        'data/cron.xml'
    ]

}
