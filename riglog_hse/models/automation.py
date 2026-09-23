from odoo import api, fields, models


class RigLogHSEIncidentAutomation(models.Model):
    _inherit = 'riglog.hse.incident'

    deadline_reminder_sent = fields.Boolean(
        string='Deadline Reminder Sent',
        default=False,
        copy=False,
    )

    def write(self, vals):
        if any(
            field in vals
            for field in (
                'state',
                'corrective_due_date',
                'corrective_owner_id',
                'corrective_action',
            )
        ):
            vals = dict(vals)
            vals['deadline_reminder_sent'] = False

        return super().write(vals)


class RigLogHSEObservationAutomation(models.Model):
    _inherit = 'riglog.hse.observation'

    deadline_reminder_sent = fields.Boolean(
        string='Deadline Reminder Sent',
        default=False,
        copy=False,
    )

    def write(self, vals):
        if any(
            field in vals
            for field in (
                'state',
                'corrective_due_date',
                'corrective_owner_id',
                'corrective_action',
            )
        ):
            vals = dict(vals)
            vals['deadline_reminder_sent'] = False

        return super().write(vals)


class RigLogHSEInspectionAutomation(models.Model):
    _inherit = 'riglog.hse.inspection'

    deadline_reminder_sent = fields.Boolean(
        string='Deadline Reminder Sent',
        default=False,
        copy=False,
    )

    def write(self, vals):
        if any(
            field in vals
            for field in (
                'state',
                'action_due_date',
                'action_owner_id',
                'action_required',
            )
        ):
            vals = dict(vals)
            vals['deadline_reminder_sent'] = False

        return super().write(vals)


class RigLogHSEAutomation(models.Model):
    _inherit = 'riglog.hse.incident'

    @api.model
    def _cron_hse_deadline_reminders(self):
        today = fields.Date.today()
        activity_type = self.env.ref(
            'mail.mail_activity_data_todo',
            raise_if_not_found=False,
        )

        if not activity_type:
            return

        hse_manager_group = self.env.ref(
            'riglog_hse.group_hse_manager',
            raise_if_not_found=False,
        )

        manager_users = (
            hse_manager_group.user_ids
            if hse_manager_group
            else self.env['res.users']
        )

        def notify(record, owner, title, message):
            if record.deadline_reminder_sent:
                return

            recipients = owner.user_id
            if not recipients:
                recipients = manager_users

            if not recipients:
                record.message_post(
                    body=f'<strong>{title}</strong><br/>{message}'
                )
                record.deadline_reminder_sent = True
                return

            model_record = self.env['ir.model']._get(record._name)

            for user in recipients:
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'res_model_id': model_record.id,
                    'res_id': record.id,
                    'user_id': user.id,
                    'date_deadline': today,
                    'summary': title,
                    'note': message,
                })

            record.message_post(
                body=f'<strong>{title}</strong><br/>{message}'
            )

            record.deadline_reminder_sent = True

        incidents = self.env['riglog.hse.incident'].search([
            ('state', '=', 'corrective_action'),
            ('corrective_due_date', '<', today),
            ('deadline_reminder_sent', '=', False),
        ])

        for record in incidents:
            notify(
                record,
                record.corrective_owner_id,
                'Overdue HSE corrective action',
                f'Incident {record.name} has an overdue corrective action.',
            )

        observations = self.env['riglog.hse.observation'].search([
            ('state', '=', 'corrective_action'),
            ('corrective_due_date', '<', today),
            ('deadline_reminder_sent', '=', False),
        ])

        for record in observations:
            notify(
                record,
                record.corrective_owner_id,
                'Overdue HSE corrective action',
                f'Safety observation {record.name} has an overdue corrective action.',
            )

        inspections = self.env['riglog.hse.inspection'].search([
            ('state', '=', 'in_progress'),
            ('action_due_date', '<', today),
            ('deadline_reminder_sent', '=', False),
        ])

        for record in inspections:
            notify(
                record,
                record.action_owner_id,
                'Overdue HSE inspection action',
                f'Inspection {record.name} has an overdue corrective action.',
            )
