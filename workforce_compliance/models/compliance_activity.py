from odoo import models, fields


class ComplianceActivity(models.Model):
    _name = 'workforce.compliance.activity'
    _description = 'Compliance Case Activity'
    _order = 'activity_date desc'

    case_id = fields.Many2one(
        'workforce.compliance.case',
        string='Compliance Case',
        required=True,
        ondelete='cascade'
    )

    activity_type = fields.Selection(
        [
            ('reported', 'Case Reported'),
            ('investigation', 'Investigation Started'),
            ('warning', 'Formal Warning Issued'),
            ('suspended', 'Employee Suspended'),
            ('resolved', 'Case Resolved'),
        ],
        string='Activity',
        required=True
    )

    description = fields.Text(
        string='Description'
    )

    activity_date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Performed By',
        default=lambda self: self.env.user,
        required=True
    )
