from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class RigLogHSEIncident(models.Model):
    _name = 'riglog.hse.incident'
    _description = 'RigLog HSE Incident'
    _inherit = ['mail.thread']
    _order = 'incident_date desc, id desc'

    name = fields.Char(
        string='Incident Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    incident_type = fields.Selection(
        [
            ('accident', 'Accident'),
            ('near_miss', 'Near Miss'),
            ('unsafe_act', 'Unsafe Act'),
            ('unsafe_condition', 'Unsafe Condition'),
            ('environmental', 'Environmental Incident'),
            ('property_damage', 'Property Damage'),
            ('fire', 'Fire'),
            ('other', 'Other'),
        ],
        string='Incident Type',
        required=True,
        tracking=True,
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
        default='low',
        tracking=True,
    )

    incident_date = fields.Datetime(
        string='Incident Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    location = fields.Char(
        string='Location',
        required=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee Involved',
    )

    reported_by_employee_id = fields.Many2one(
        'hr.employee',
        string='Reported By',
        default=lambda self: self.env.user.employee_id,
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    description = fields.Text(
        string='Incident Description',
        required=True,
    )

    immediate_action = fields.Text(
        string='Immediate Action Taken',
    )

    investigator_id = fields.Many2one(
        'hr.employee',
        string='Investigator',
    )

    investigation_findings = fields.Text(
        string='Investigation Findings',
    )

    root_cause = fields.Text(
        string='Root Cause',
    )

    corrective_action = fields.Text(
        string='Corrective Action',
    )

    corrective_owner_id = fields.Many2one(
        'hr.employee',
        string='Corrective Action Owner',
    )

    corrective_due_date = fields.Date(
        string='Corrective Action Due Date',
    )

    closure_note = fields.Text(
        string='Closure Note',
    )

    closed_date = fields.Datetime(
        string='Closed Date',
        readonly=True,
    )

    state = fields.Selection(
        [
            ('reported', 'Reported'),
            ('investigation', 'Investigation'),
            ('corrective_action', 'Corrective Action'),
            ('closed', 'Closed'),
        ],
        string='Status',
        required=True,
        default='reported',
        tracking=True,
    )

    def write(self, vals):
        if 'state' in vals and not self.env.context.get('riglog_workflow'):
            if any(record.state != vals['state'] for record in self):
                raise AccessError(
                    'HSE Incident status can only be changed through the approved workflow actions.'
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'riglog.hse.incident'
                ) or 'New'

        return super().create(vals_list)

    def action_start_investigation(self):
        for record in self:
            if record.state != 'reported':
                raise UserError(
                    'Only reported incidents can be moved to investigation.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'investigation'})

    def action_start_corrective_action(self):
        for record in self:
            if record.state != 'investigation':
                raise UserError(
                    'Only incidents under investigation can move to corrective action.'
                )

            if not record.investigation_findings:
                raise UserError(
                    'Enter the investigation findings before starting corrective action.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'corrective_action'})

    def action_close(self):
        for record in self:
            if record.state != 'corrective_action':
                raise UserError(
                    'Only incidents in corrective action can be closed.'
                )

            if not record.corrective_action:
                raise UserError(
                    'Enter the corrective action before closing the incident.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'closed',
                'closed_date': fields.Datetime.now(),
            })

    def action_reset_reported(self):
        for record in self:
            if record.state != 'closed':
                raise UserError(
                    'Only closed incidents can be reset.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'reported',
                'closed_date': False,
            })


class RigLogHSEIncidentProject(models.Model):
    _inherit = 'project.project'

    riglog_hse_incident_count = fields.Integer(
        string='HSE Incidents',
        compute='_compute_riglog_hse_incident_count',
    )

    def _compute_riglog_hse_incident_count(self):
        Incident = self.env['riglog.hse.incident']

        for project in self:
            project.riglog_hse_incident_count = Incident.search_count([
                ('project_id', '=', project.id)
            ])

    def action_view_riglog_hse_incidents(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'HSE Incidents',
            'res_model': 'riglog.hse.incident',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }


class RigLogHSEObservation(models.Model):
    _name = 'riglog.hse.observation'
    _description = 'RigLog HSE Safety Observation'
    _inherit = ['mail.thread']
    _order = 'observation_date desc, id desc'

    name = fields.Char(
        string='Observation Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    observation_type = fields.Selection(
        [
            ('safe', 'Safe Observation'),
            ('unsafe_act', 'Unsafe Act'),
            ('unsafe_condition', 'Unsafe Condition'),
            ('environmental', 'Environmental Observation'),
        ],
        string='Observation Type',
        required=True,
        tracking=True,
    )

    category = fields.Selection(
        [
            ('ppe', 'PPE'),
            ('housekeeping', 'Housekeeping'),
            ('equipment', 'Equipment'),
            ('work_practice', 'Work Practice'),
            ('fire', 'Fire Safety'),
            ('environment', 'Environment'),
            ('other', 'Other'),
        ],
        string='Category',
        required=True,
        tracking=True,
    )

    severity = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Priority',
        required=True,
        default='low',
        tracking=True,
    )

    observation_date = fields.Datetime(
        string='Observation Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    location = fields.Char(
        string='Location',
        required=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee Involved',
    )

    reported_by_employee_id = fields.Many2one(
        'hr.employee',
        string='Reported By',
        default=lambda self: self.env.user.employee_id,
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    description = fields.Text(
        string='Observation',
        required=True,
    )

    immediate_action = fields.Text(
        string='Immediate Action Taken',
    )

    corrective_action = fields.Text(
        string='Corrective Action',
    )

    corrective_owner_id = fields.Many2one(
        'hr.employee',
        string='Corrective Action Owner',
    )

    corrective_due_date = fields.Date(
        string='Corrective Action Due Date',
    )

    closure_note = fields.Text(
        string='Closure Note',
    )

    closed_date = fields.Datetime(
        string='Closed Date',
        readonly=True,
    )

    state = fields.Selection(
        [
            ('reported', 'Reported'),
            ('corrective_action', 'Corrective Action'),
            ('closed', 'Closed'),
        ],
        string='Status',
        required=True,
        default='reported',
        tracking=True,
    )

    def write(self, vals):
        if 'state' in vals and not self.env.context.get('riglog_workflow'):
            if any(record.state != vals['state'] for record in self):
                raise AccessError(
                    'Safety Observation status can only be changed through the approved workflow actions.'
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'riglog.hse.observation'
                ) or 'New'

        return super().create(vals_list)

    def action_start_corrective_action(self):
        for record in self:
            if record.state != 'reported':
                raise UserError(
                    'Only reported observations can move to corrective action.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'corrective_action'})

    def action_close(self):
        for record in self:
            if record.state != 'corrective_action':
                raise UserError(
                    'Only observations in corrective action can be closed.'
                )

            if not record.corrective_action:
                raise UserError(
                    'Enter the corrective action before closing the observation.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'closed',
                'closed_date': fields.Datetime.now(),
            })

    def action_reset_reported(self):
        for record in self:
            if record.state != 'closed':
                raise UserError(
                    'Only closed observations can be reset.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'reported',
                'closed_date': False,
            })


class RigLogHSEProjectObservation(models.Model):
    _inherit = 'project.project'

    riglog_hse_observation_count = fields.Integer(
        string='Safety Observations',
        compute='_compute_riglog_hse_observation_count',
    )

    def _compute_riglog_hse_observation_count(self):
        Observation = self.env['riglog.hse.observation']

        for project in self:
            project.riglog_hse_observation_count = Observation.search_count([
                ('project_id', '=', project.id)
            ])

    def action_view_riglog_hse_observations(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Safety Observations',
            'res_model': 'riglog.hse.observation',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }
