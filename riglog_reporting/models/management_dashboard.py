from odoo import fields, models


class RigLogManagementDashboard(models.Model):
    _name = 'riglog.management.dashboard'
    _description = 'RigLog Management KPI Dashboard'

    name = fields.Char(
        string='Dashboard',
        required=True,
        default='RigLog Management KPIs',
        readonly=True,
    )

    active_projects = fields.Integer(
        string='Active Projects',
        compute='_compute_kpis',
    )

    pending_purchase_requests = fields.Integer(
        string='Purchase Requests Pending Approval',
        compute='_compute_kpis',
    )

    approved_awaiting_rfq = fields.Integer(
        string='Approved Requests Awaiting RFQ',
        compute='_compute_kpis',
    )

    open_material_handovers = fields.Integer(
        string='Open Material Handovers',
        compute='_compute_kpis',
    )

    open_hse_incidents = fields.Integer(
        string='Open HSE Incidents',
        compute='_compute_kpis',
    )

    open_safety_observations = fields.Integer(
        string='Open Safety Observations',
        compute='_compute_kpis',
    )

    inspections_in_progress = fields.Integer(
        string='Inspections In Progress',
        compute='_compute_kpis',
    )

    overdue_corrective_actions = fields.Integer(
        string='Overdue Corrective Actions',
        compute='_compute_kpis',
    )

    employees = fields.Integer(
        string='Employees',
        compute='_compute_kpis',
    )

    vehicles = fields.Integer(
        string='Vehicles',
        compute='_compute_kpis',
    )

    attendance_today = fields.Integer(
        string='Attendance Today',
        compute='_compute_kpis',
    )

    pending_leave_requests = fields.Integer(
        string='Pending Leave Requests',
        compute='_compute_kpis',
    )

    def _compute_kpis(self):
        today = fields.Date.today()

        Project = self.env['project.project']
        PurchaseRequest = self.env['riglog.purchase.request']
        MaterialHandover = self.env['riglog.material.handover']
        Incident = self.env['riglog.hse.incident']
        Observation = self.env['riglog.hse.observation']
        Inspection = self.env['riglog.hse.inspection']
        Employee = self.env['hr.employee']
        Vehicle = self.env['fleet.vehicle']
        Attendance = self.env['hr.attendance']
        Leave = self.env['hr.leave']

        active_projects = Project.search_count([
            ('active', '=', True),
        ])

        pending_purchase_requests = PurchaseRequest.search_count([
            ('state', '=', 'submitted'),
        ])

        approved_awaiting_rfq = PurchaseRequest.search_count([
            ('state', '=', 'approved'),
            ('purchase_order_id', '=', False),
        ])

        open_material_handovers = MaterialHandover.search_count([
            ('state', '=', 'draft'),
        ])

        open_hse_incidents = Incident.search_count([
            ('state', '!=', 'closed'),
        ])

        open_safety_observations = Observation.search_count([
            ('state', '!=', 'closed'),
        ])

        inspections_in_progress = Inspection.search_count([
            ('state', '=', 'in_progress'),
        ])

        overdue_incidents = Incident.search_count([
            ('state', '=', 'corrective_action'),
            ('corrective_due_date', '<', today),
        ])

        overdue_observations = Observation.search_count([
            ('state', '=', 'corrective_action'),
            ('corrective_due_date', '<', today),
        ])

        overdue_inspections = Inspection.search_count([
            ('state', '=', 'in_progress'),
            ('action_due_date', '<', today),
        ])

        employees = Employee.search_count([
            ('active', '=', True),
        ])

        vehicles = Vehicle.search_count([
            ('active', '=', True),
        ])

        attendance_today = Attendance.search_count([
            ('check_in', '>=', fields.Datetime.start_of(fields.Datetime.now(), 'day')),
        ])

        pending_leave_requests = Leave.search_count([
            ('state', 'in', ('confirm', 'validate1')),
        ])

        for record in self:
            record.active_projects = active_projects
            record.pending_purchase_requests = pending_purchase_requests
            record.approved_awaiting_rfq = approved_awaiting_rfq
            record.open_material_handovers = open_material_handovers
            record.open_hse_incidents = open_hse_incidents
            record.open_safety_observations = open_safety_observations
            record.inspections_in_progress = inspections_in_progress
            record.overdue_corrective_actions = (
                overdue_incidents
                + overdue_observations
                + overdue_inspections
            )
            record.employees = employees
            record.vehicles = vehicles
            record.attendance_today = attendance_today
            record.pending_leave_requests = pending_leave_requests
