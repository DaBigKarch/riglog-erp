{
    'name': 'RigLog Project Integration',
    'version': '19.0.1.0.0',
    'summary': 'Connect RigLog projects with procurement and materials',
    'description': """
RigLog Project Integration
==========================
Links projects to Purchase Requests and Material Handovers,
and carries the project through to the native Purchase Order.
    """,
    'author': 'Vecora Technologies',
    'license': 'LGPL-3',
    'category': 'Operations/Project',
    'depends': [
        'project',
        'project_purchase',
        'riglog_procurement',
        'riglog_materials',
    ],
    'data': [
        'views/project_links_views.xml',
    ],
    'application': True,
    'installable': True,
}
