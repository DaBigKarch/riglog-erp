from odoo import api, fields, models
from odoo.exceptions import UserError


class RigLogMaterialHandover(models.Model):
    _name = 'riglog.material.handover'
    _description = 'RigLog Material Handover'
    _inherit = ['mail.thread']
    _order = 'handover_date desc, id desc'

    name = fields.Char(
        string='Handover Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )

    picking_id = fields.Many2one(
        'stock.picking',
        string='Receipt',
        required=True,
        domain="[('state', '=', 'done'), ('picking_type_code', '=', 'incoming')]",
        tracking=True,
    )

    handover_date = fields.Datetime(
        string='Handover Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    handed_to_employee_id = fields.Many2one(
        'hr.employee',
        string='Handed To',
        tracking=True,
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='handed_to_employee_id.department_id',
        store=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    notes = fields.Text(
        string='Notes',
    )

    line_ids = fields.One2many(
        'riglog.material.handover.line',
        'handover_id',
        string='Materials',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('handed_over', 'Handed Over'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'riglog.material.handover'
                ) or 'New'
        return super().create(vals_list)

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if not self.picking_id:
            self.line_ids = [(5, 0, 0)]
            return

        commands = [(5, 0, 0)]

        for move_line in self.picking_id.move_line_ids.filtered(
            lambda ml: ml.product_id and ml.quantity > 0
        ):
            commands.append((0, 0, {
                'product_id': move_line.product_id.id,
                'quantity': move_line.quantity,
                'uom_id': move_line.product_uom_id.id,
            }))

        self.line_ids = commands

    def action_mark_handed_over(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    'Only draft handovers can be marked as handed over.'
                )

            if not record.picking_id:
                raise UserError('A completed receipt is required.')

            if record.picking_id.state != 'done':
                raise UserError(
                    'The linked receipt must be completed before handover.'
                )

            if not record.handed_to_employee_id:
                raise UserError(
                    'Select the employee receiving the materials.'
                )

            if not record.line_ids:
                raise UserError(
                    'Add at least one material to the handover.'
                )

            record.state = 'handed_over'


class RigLogMaterialHandoverLine(models.Model):
    _name = 'riglog.material.handover.line'
    _description = 'RigLog Material Handover Line'

    handover_id = fields.Many2one(
        'riglog.material.handover',
        string='Handover',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Material',
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
        required=True,
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise UserError(
                    'Handover quantity must be greater than zero.'
                )

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_create_riglog_handover(self):
        self.ensure_one()

        if self.state != 'done':
            raise UserError(
                'A handover can only be created from a completed receipt.'
            )

        if self.picking_type_code != 'incoming':
            raise UserError(
                'A handover can only be created from an incoming receipt.'
            )

        handover = self.env['riglog.material.handover'].create({
            'picking_id': self.id,
            'company_id': self.company_id.id,
        })

        lines = []

        for move_line in self.move_line_ids.filtered(
            lambda ml: ml.product_id and ml.quantity > 0
        ):
            lines.append((0, 0, {
                'product_id': move_line.product_id.id,
                'quantity': move_line.quantity,
                'uom_id': move_line.product_uom_id.id,
            }))

        handover.line_ids = lines

        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Handover',
            'res_model': 'riglog.material.handover',
            'view_mode': 'form',
            'res_id': handover.id,
        }
