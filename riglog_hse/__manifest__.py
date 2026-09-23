{
    'name': 'RigLog HSE',
    'version': '19.0.1.0.0',
    'summary': 'HSE incident, near-miss and corrective action management',
    'description': """
RigLog HSE
==========
Incident and near-miss register with investigation,
corrective action and closure workflow.
    """,
    'author': 'Vecora Technologies',
    'license': 'LGPL-3',
    'category': 'Operations',
    'depends': [
        'base',
        'hr',
        'project',
        'mail',
        'riglog_procurement',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/automation.xml',
        'views/hse_incident_views.xml',
        'views/hse_inspection_views.xml',
    ],
    'application': True,
    'installable': True,
}
