from odoo import api, models, fields
from odoo.exceptions import UserError


class ComplianceCase(models.Model):
    _name = 'workforce.compliance.case'
    _description = 'Workplace Compliance Case'
    _order = 'create_date desc'

    name = fields.Char(
        string='Case Reference',
        required=True,
        copy=False,
        default='New'
    )

    employee_name = fields.Char(
        string='Employee',
        required=True
    )

    incident_date = fields.Date(
        string='Incident Date',
        required=True
    )

    violation_type = fields.Selection(
        [
            ('attendance', 'Attendance Violation'),
            ('conduct', 'Misconduct'),
            ('performance', 'Performance Issue'),
            ('safety', 'Safety Violation'),
            ('policy', 'Policy Violation'),
            ('other', 'Other'),
        ],
        string='Violation Type',
        required=True,
        default='other'
    )

    severity = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Severity',
        required=True,
        default='medium'
    )

    investigator_id = fields.Many2one(
        'res.users',
        string='Assigned Investigator'
    )

    warning_date = fields.Date(
        string='Warning Date'
    )

    suspension_start = fields.Date(
        string='Suspension Start'
    )

    suspension_end = fields.Date(
        string='Suspension End'
    )

    resolution_date = fields.Date(
        string='Resolution Date'
    )

    description = fields.Text(
        string='Incident Description',
        required=True
    )

    state = fields.Selection(
        [
            ('reported', 'Reported'),
            ('investigation', 'Under Investigation'),
            ('warning', 'Formal Warning'),
            ('suspended', 'Suspended'),
            ('resolved', 'Resolved'),
        ],
        string='Status',
        default='reported',
        required=True
    )

    notes = fields.Text(
        string='Investigation Notes'
    )

    resolution_notes = fields.Text(
        string='Resolution Notes'
    )

    activity_ids = fields.One2many(
        'workforce.compliance.activity',
        'case_id',
        string='Case Activity',
        readonly=True
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._log_activity(
            'reported',
            'Compliance case reported and created.'
        )
        return record

    def _log_activity(self, activity_type, description):
        self.env['workforce.compliance.activity'].create({
            'case_id': self.id,
            'activity_type': activity_type,
            'description': description,
        })

    def action_start_investigation(self):
        for record in self:
            if record.state != 'reported':
                raise UserError(
                    'Only reported cases can be moved to investigation.'
                )

            record.write({
                'state': 'investigation'
            })

            record._log_activity(
                'investigation',
                'Investigation started for this compliance case.'
            )

    def action_issue_warning(self):
        for record in self:
            if record.state != 'investigation':
                raise UserError(
                    'A case must be under investigation before a formal warning can be issued.'
                )

            record.write({
                'state': 'warning',
                'warning_date': fields.Date.today(),
            })

            record._log_activity(
                'warning',
                'Formal warning issued for this compliance case.'
            )

    def action_suspend(self):
        for record in self:
            if record.state != 'warning':
                raise UserError(
                    'A case must have a formal warning before suspension.'
                )

            record.write({
                'state': 'suspended',
                'suspension_start': fields.Date.today(),
            })

            record._log_activity(
                'suspended',
                'Employee suspended as part of the disciplinary process.'
            )

    def action_resolve(self):
        for record in self:
            if record.state != 'suspended':
                raise UserError(
                    'Only suspended cases can be resolved.'
                )

            record.write({
                'state': 'resolved',
                'resolution_date': fields.Date.today(),
            })

            record._log_activity(
                'resolved',
                'Compliance case resolved and closed.'
            )
