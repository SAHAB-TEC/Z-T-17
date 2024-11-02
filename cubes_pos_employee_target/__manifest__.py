{
    'name': "Cubes POS Employee Target",
    'version': '1.0',
    'author': "Cubes POS Employee Target",
    'description': """Cubes POS Employee Target""",
    'depends': [
        'base',
        'point_of_sale',
        'hr',
        'hr_contract',
        'hr_attendance',
        'hr_payroll',
        'pos_hr'
    ],
    'assets': {
        'web.assets_qweb': [
            'cubes_pos_employee_target/static/src/xml/pos_employee.xml'
        ],
        'point_of_sale.assets': [
            'cubes_pos_employee_target/static/src/js/pos_employee.js',
            'cubes_pos_employee_target/static/src/xml/pos_employee.xml'
        ],
    },
    # 'qweb': [
    #     'static/src/xml/pos_employee.xml',
    # ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payroll.xml',
        'views/payslip_view.xml',

    ],

    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
