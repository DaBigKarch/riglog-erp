from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        domain="[('company_id', 'in', [company_id, False])]",
        tracking=True,
    )


class RigLogProject(models.Model):
    _inherit = 'project.project'

    riglog_vehicle_count = fields.Integer(
        string='Vehicles',
        compute='_compute_riglog_vehicle_count',
    )

    def _compute_riglog_vehicle_count(self):
        Vehicle = self.env['fleet.vehicle']

        for project in self:
            project.riglog_vehicle_count = Vehicle.search_count([
                ('project_id', '=', project.id)
            ])

    def action_view_riglog_vehicles(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'res_model': 'fleet.vehicle',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }
