from odoo import models, fields, _


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')


class WhatsappList(models.Model):
    _name = 'whatsapp.list'

    name = fields.Char(string='Name')
    whatsapp_line_ids = fields.One2many('whatsapp.list.line', 'whatsapp_list_id')
    contact_count = fields.Integer(compute='_contact_count_func')

    def _contact_count_func(self):
        for rec in self:
            rec.contact_count = len(rec.whatsapp_line_ids.ids)

    def name_get(self):
        return [(list.id, "%s (%s)" % (list.name, list.contact_count)) for list in self]

    def action_open_contact_list(self):
        return {
            'name': _('Contact List'),
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('id', 'in', [rec.partner_id.id for rec in self.whatsapp_line_ids])],
        }


class WhatsappListLine(models.Model):
    _name = 'whatsapp.list.line'

    name = fields.Char(string='Name')
    whatsapp_list_id = fields.Many2one('whatsapp.list')
    partner_id = fields.Many2one('res.partner')
    phone = fields.Char(related='partner_id.phone', string='Phone')
    mobile = fields.Char(related='partner_id.mobile', string='Mobile')

    def name_get(self):
        return [(list.id, "%s" % (list.partner_id.name)) for list in self]

