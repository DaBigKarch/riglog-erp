from odoo import fields, models
from odoo.exceptions import UserError


class RigLogPurchaseRequestRFQWizard(models.TransientModel):
    _name = 'riglog.purchase.request.rfq.wizard'
    _description = 'Create RFQ from RigLog Purchase Request'

    request_id = fields.Many2one(
        'riglog.purchase.request',
        string='Purchase Request',
        required=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
    )

    def action_create_rfq(self):
        self.ensure_one()

        request = self.request_id

        if request.state != 'approved':
            raise UserError(
                'Only approved purchase requests can create an RFQ.'
            )

        if request.purchase_order_id:
            raise UserError(
                'An RFQ has already been created for this purchase request.'
            )

        if not request.line_ids:
            raise UserError(
                'The purchase request has no requested items.'
            )

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'company_id': request.company_id.id,
            'origin': request.name,
        })

        for line in request.line_ids:
            uom = line.uom_id or (
                line.product_id.uom_id if line.product_id else False
            )

            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': line.product_id.id or False,
                'name': line.description,
                'product_qty': line.quantity,
                'product_uom_id': uom.id if uom else False,
                'price_unit': 0.0,
                'date_planned': fields.Datetime.now(),
            })

        request.purchase_order_id = purchase_order.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Request for Quotation',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
        }
