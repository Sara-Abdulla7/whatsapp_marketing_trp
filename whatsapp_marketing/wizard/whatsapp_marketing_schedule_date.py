from odoo import fields, models, _
from odoo.exceptions import UserError


class WhatsappMarketingScheduleDate(models.TransientModel):
    _name = "whatsapp.marketing.schedule.date"
    _description = "schedule a whatsapp marketing"

    schedule_date = fields.Datetime(string='Scheduled for')
    whatsapp_marketing_id = fields.Many2one('whatsapp.marketing', required=True)

    def action_schedule_date(self):
        partner_ids = self.whatsapp_marketing_id.get_recipients() if self.whatsapp_marketing_id.mailing_model_name != 'mailing.list' else self.whatsapp_marketing_id.get_whatsapp_list_contact()
        print('partner', partner_ids)
        print('partner', self.whatsapp_marketing_id.get_recipients())
        if len(partner_ids) < 1:
            raise UserError(_('There are no Clients Selected'))

        cron = self.env['ir.cron'].create({
            'name': self.whatsapp_marketing_id.name or 'Whatsapp Marketing',
            'model_id': self.env.ref('whatsapp_marketing.model_whatsapp_marketing').id,
            'state': 'code',
            'code': 'model.search([("id", "=", %s)])._process_whatsapp_marketing_queue()' % self.whatsapp_marketing_id.id,
            'interval_number': 1,
            'interval_type': 'days',
            'numbercall': 1,
            'nextcall': self.schedule_date or fields.Datetime.now(),
            'doall': False,
        })
        self.whatsapp_marketing_id.write(
            {'next_departure': self.schedule_date, 'ir_cron_id': cron.id, 'state': 'in_queue'})
