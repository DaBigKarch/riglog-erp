from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class RigLogPurchaseRequest(models.Model):
    _name = 'riglog.purchase.request'
    _description = 'RigLog Purchase Request'
    _inherit = ['mail.thread']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Requested By',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )

    requested_by_user_id = fields.Many2one(
        'res.users',
        string='Requesting User',
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    request_date = fields.Datetime(
        string='Request Date',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )

    required_date = fields.Date(
        string='Required By',
    )

    justification = fields.Text(
        string='Justification',
    )

    line_ids = fields.One2many(
        'riglog.purchase.request.line',
        'request_id',
        string='Requested Items',
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='RFQ / Purchase Order',
        readonly=True,
        copy=False,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
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
                    'Purchase Request status can only be changed through the approved workflow actions.'
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'riglog.purchase.request'
                ) or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('Only draft requests can be submitted.')

            if not record.line_ids:
                raise UserError(
                    'Add at least one requested item before submitting.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'submitted'})

    def action_approve(self):
        if not (
            self.env.user.has_group('base.group_system')
            or self.env.user.has_group(
                'riglog_procurement.group_procurement_approver'
            )
        ):
            raise AccessError(
                'You do not have permission to approve RigLog purchase requests.'
            )

        for record in self:
            if record.state != 'submitted':
                raise UserError('Only submitted requests can be approved.')

            record.with_context(riglog_workflow=True).write({'state': 'approved'})

    def action_reject(self):
        if not (
            self.env.user.has_group('base.group_system')
            or self.env.user.has_group(
                'riglog_procurement.group_procurement_approver'
            )
        ):
            raise AccessError(
                'You do not have permission to reject RigLog purchase requests.'
            )

        for record in self:
            if record.state != 'submitted':
                raise UserError('Only submitted requests can be rejected.')

            record.with_context(riglog_workflow=True).write({'state': 'rejected'})

    def action_reset_draft(self):
        for record in self:
            if record.state != 'rejected':
                raise UserError(
                    'Only rejected requests can be reset to draft.'
                )

            if not (
                self.env.user.has_group('base.group_system')
                or self.env.user.has_group(
                    'riglog_procurement.group_procurement_user'
                )
            ):
                raise AccessError(
                    'You do not have permission to reset this request.'
                )

            record.with_context(riglog_workflow=True).write({'state': 'draft'})

    def action_create_rfq(self):
        self.ensure_one()

        if self.state != 'approved':
            raise UserError(
                'Only approved purchase requests can create an RFQ.'
            )

        if self.purchase_order_id:
            raise UserError(
                'An RFQ has already been created for this request.'
            )

        if not self.line_ids:
            raise UserError(
                'The purchase request has no requested items.'
            )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ',
            'res_model': 'riglog.purchase.request.rfq.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }

    def action_open_rfq(self):
        self.ensure_one()

        if not self.purchase_order_id:
            raise UserError(
                'No RFQ has been created for this request.'
            )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Request for Quotation',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_order_id.id,
        }


class RigLogPurchaseRequestLine(models.Model):
    _name = 'riglog.purchase.request.line'
    _description = 'RigLog Purchase Request Line'
    _order = 'id'

    request_id = fields.Many2one(
        'riglog.purchase.request',
        string='Purchase Request',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    description = fields.Char(
        string='Description',
        required=True,
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise UserError(
                    'Requested quantity must be greater than zero.'
                )
