from odoo import api, fields, models


class RigLogPurchaseRequest(models.Model):
    _inherit = 'riglog.purchase.request'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        check_company=True,
        domain="[('is_template', '=', False)]",
    )


class RigLogMaterialHandover(models.Model):
    _inherit = 'riglog.material.handover'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='picking_id.move_ids.purchase_line_id.order_id.project_id',
        store=True,
        readonly=True,
    )


class RigLogPurchaseRequestRFQWizard(models.TransientModel):
    _inherit = 'riglog.purchase.request.rfq.wizard'

    def action_create_rfq(self):
        self.ensure_one()

        action = super().action_create_rfq()

        purchase_order_id = action.get('res_id') if isinstance(action, dict) else False

        if purchase_order_id and self.request_id.project_id:
            self.env['purchase.order'].browse(
                purchase_order_id
            ).project_id = self.request_id.project_id.id

        return action


class RigLogProject(models.Model):
    _inherit = 'project.project'

    riglog_purchase_request_count = fields.Integer(
        string='Purchase Requests',
        compute='_compute_riglog_counts',
    )

    riglog_handover_count = fields.Integer(
        string='Material Handovers',
        compute='_compute_riglog_counts',
    )

    def _compute_riglog_counts(self):
        PurchaseRequest = self.env['riglog.purchase.request']
        MaterialHandover = self.env['riglog.material.handover']

        for project in self:
            project.riglog_purchase_request_count = PurchaseRequest.search_count([
                ('project_id', '=', project.id)
            ])

            project.riglog_handover_count = MaterialHandover.search_count([
                ('project_id', '=', project.id)
            ])

    def action_view_riglog_purchase_requests(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Requests',
            'res_model': 'riglog.purchase.request',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }

    def action_view_riglog_handovers(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Handovers',
            'res_model': 'riglog.material.handover',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
        }
