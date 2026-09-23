from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class RigLogHSEInspection(models.Model):
    _name = 'riglog.hse.inspection'
    _description = 'RigLog HSE Safety Inspection'
    _inherit = ['mail.thread']
    _order = 'inspection_date desc, id desc'

    name = fields.Char(
        string='Inspection Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    inspection_type = fields.Selection(
        [
            ('site', 'Site Inspection'),
            ('workshop', 'Workshop Inspection'),
            ('equipment', 'Equipment Inspection'),
            ('vehicle', 'Vehicle Inspection'),
            ('housekeeping', 'Housekeeping Inspection'),
            ('environmental', 'Environmental Inspection'),
            ('other', 'Other'),
        ],
        string='Inspection Type',
        required=True,
        tracking=True,
    )

    inspection_date = fields.Datetime(
        string='Inspection Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    location = fields.Char(
        string='Location',
        required=True,
    )

    inspector_id = fields.Many2one(
        'hr.employee',
        string='Inspector',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    summary = fields.Text(
        string='Summary',
    )

    findings = fields.Text(
        string='Findings',
    )

    overall_result = fields.Selection(
        [
            ('satisfactory', 'Satisfactory'),
            ('observation_required', 'Observation Required'),
            ('action_required', 'Action Required'),
        ],
        string='Overall Result',
        tracking=True,
    )

    action_required = fields.Text(
        string='Corrective Action Required',
    )

    action_owner_id = fields.Many2one(
        'hr.employee',
        string='Action Owner',
    )

    action_due_date = fields.Date(
        string='Action Due Date',
    )

    closure_note = fields.Text(
        string='Closure Note',
    )

    completed_date = fields.Datetime(
        string='Completed Date',
        readonly=True,
    )

    line_ids = fields.One2many(
        'riglog.hse.inspection.line',
        'inspection_id',
        string='Checklist',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
    )

    def write(self, vals):
        if 'state' in vals and not self.env.context.get('riglog_workflow'):
            if any(record.state != vals['state'] for record in self):
                raise AccessError(
                    'HSE Inspection status can only be changed through the approved workflow actions.'
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'riglog.hse.inspection'
                ) or 'New'

        return super().create(vals_list)

    def action_start(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    'Only draft inspections can be started.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'in_progress'})

    def action_complete(self):
        for record in self:
            if record.state != 'in_progress':
                raise UserError(
                    'Only inspections in progress can be completed.'
                )

            if not record.line_ids:
                raise UserError(
                    'Add at least one checklist item before completing the inspection.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'completed',
                'completed_date': fields.Datetime.now(),
            })

    def action_reset(self):
        for record in self:
            if record.state != 'completed':
                raise UserError(
                    'Only completed inspections can be reset.'
                )

            record.with_context(riglog_workflow=True).write({
                'state': 'draft',
                'completed_date': False,
            })


class RigLogHSEInspectionLine(models.Model):
    _name = 'riglog.hse.inspection.line'
    _description = 'RigLog HSE Inspection Checklist Line'

    inspection_id = fields.Many2one(
        'riglog.hse.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade',
    )

    checklist_item = fields.Char(
        string='Checklist Item',
        required=True,
    )

    result = fields.Selection(
        [
            ('compliant', 'Compliant'),
            ('non_compliant', 'Non-Compliant'),
            ('not_applicable', 'Not Applicable'),
        ],
        string='Result',
        required=True,
        default='compliant',
    )

    comment = fields.Char(
        string='Comment',
    )


class RigLogHSEProjectInspection(models.Model):
    _inherit = 'project.project'

    riglog_hse_inspection_count = fields.Integer(
        string='Safety Inspections',
        compute='_compute_riglog_hse_inspection_count',
    )

    def _compute_riglog_hse_inspection_count(self):
        Inspection = self.env['riglog.hse.inspection']

        for project in self:
            project.riglog_hse_inspection_count = Inspection.search_count([
                ('project_id', '=', project.id)
            ])

    def action_view_riglog_hse_inspections(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Safety Inspections',
            'res_model': 'riglog.hse.inspection',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }
