{
    'name': 'RigLog Materials',
    'version': '19.0.1.0.0',
    'summary': 'Materials handover management for RigLog ERP',
    'description': """
RigLog Materials
================
Records material handovers against completed Odoo stock receipts.
    """,
    'author': 'Vecora Technologies',
    'license': 'LGPL-3',
    'category': 'Operations/Inventory',
    'depends': [
        'base',
        'stock',
        'hr',
        'mail',
        'riglog_procurement',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/material_handover_views.xml',
        'views/stock_picking_views.xml',
    ],
    'application': True,
    'installable': True,
}
