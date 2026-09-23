from odoo import fields, models


class RigLogPurchaseRequestAutomation(models.Model):
    _inherit = 'riglog.purchase.request'

    approval_notification_sent = fields.Boolean(
        string='Approval Notification Sent',
        default=False,
        copy=False,
    )

    def action_approve(self):
        result = super().action_approve()

        activity_type = self.env.ref(
            'mail.mail_activity_data_todo',
            raise_if_not_found=False,
        )

        approver_group = self.env.ref(
            'riglog_procurement.group_procurement_approver',
            raise_if_not_found=False,
        )

        if not activity_type or not approver_group:
            return result

        model_record = self.env['ir.model']._get(
            'riglog.purchase.request'
        )

        for record in self:
            if record.approval_notification_sent:
                continue

            users = approver_group.user_ids

            for user in users:
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'res_model_id': model_record.id,
                    'res_id': record.id,
                    'user_id': user.id,
                    'date_deadline': fields.Date.today(),
                    'summary': 'Approved Purchase Request',
                    'note': (
                        f'Purchase Request {record.name} has been approved '
                        'and is ready for procurement processing / RFQ creation.'
                    ),
                })

            record.message_post(
                body=(
                    f'<strong>Purchase Request Approved</strong><br/>'
                    f'{record.name} is now ready for procurement processing.'
                )
            )

            record.approval_notification_sent = True

        return result
