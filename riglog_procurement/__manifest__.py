{
    'name': 'RigLog Procurement',
    'version': '19.0.1.0.0',
    'summary': 'Internal procurement request management for RigLog ERP',
    'description': """
RigLog Procurement
==================
Initial internal Purchase Request workflow for RigLog ERP.
    """,
    'author': 'Vecora Technologies',
    'license': 'LGPL-3',
    'category': 'Operations/Purchase',
    'depends': [
        'base',
        'hr',
        'purchase',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/purchase_request_views.xml',
        'wizard/purchase_request_rfq_views.xml',
    ],
    'application': True,
    'installable': True,
}
