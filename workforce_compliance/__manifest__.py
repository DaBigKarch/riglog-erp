{
    'name': 'Workforce Compliance',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'Workplace compliance and disciplinary management',
    'description': """
        Workforce Compliance Management

        Manages workplace compliance cases, investigations,
        disciplinary actions, and case resolution.
    """,
    'author': 'Vecora Technologies',
    'website': 'https://vecora.siwesone.ng',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/compliance_case_views.xml',
        'views/compliance_menu.xml',
    ],
    'installable': True,
    'application': True,
}
