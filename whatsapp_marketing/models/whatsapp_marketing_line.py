from odoo import models, fields, _


class WhatsappMarketingLine(models.Model):
    _name = 'whatsapp.marketing.line'
    _description = 'Whatsapp marketing.line'

    name = fields.Many2one('whatsapp.marketing', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Send TO')
    phone = fields.Char(string='Phone OR Mobile')
    state_description = fields.Char(string='State Description')
    state = fields.Selection([('sent', 'Sent'), ('failure', 'Failure')], string='State')

    def open_client_view(self):
        return {
            'name': _('Client'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'res.partner',
            'domain': [('id', '=', self.partner_id.id)],

        }



