from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from ast import literal_eval
import requests
import json
import logging
import time

_logger = logging.getLogger(__name__)



class WhatsappMarketing(models.Model):
    """ Whatsapp Marketing models the sending of messages to a list of recipients ."""
    _name = 'whatsapp.marketing'
    _description = 'Whatsapp Marketing'
    _inherit = ['mail.thread',
                'mail.activity.mixin', ]

    name = fields.Char(string='Name')
    message = fields.Char(string='Message')

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('in_queue', 'In Queue'),
         ('done', 'Sent'), ('cancel', 'Cancel')],
        string='Status',
        default='draft', required=True,
        copy=False, tracking=True,
        group_expand='_group_expand_states')

    mailing_model_id = fields.Many2one(
        'ir.model', string='Recipients Model',
        ondelete='cascade', required=True,
        domain=[('is_mailing_enabled', '=', True)],
        default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)

    mailing_model_real = fields.Char(
        string='Recipients Real Model', compute='_compute_mailing_model_real')

    mailing_domain = fields.Char(string='Domain')
    sent_message_count = fields.Integer(compute='sent_message_count_func')
    failure_message_count = fields.Integer(compute='failure_message_count_func')
    attachment_ids = fields.Many2many('ir.attachment')
    active = fields.Boolean(default=True, tracking=True)

    contact_list_ids = fields.Many2many('mailing.list', string='Mailing Lists')
    mailing_model_name = fields.Char(
        string='Recipients Model Name',
        related='mailing_model_id.model', readonly=True, related_sudo=True)
    whatsapp_list = fields.Many2many('whatsapp.list')
    next_departure = fields.Datetime(string='Scheduled date')
    ir_cron_id = fields.Many2one('ir.cron')

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('mailing_model_id')
    def _compute_mailing_model_real(self):
        for mailing in self:
            mailing.mailing_model_real = 'mailing.contact' if mailing.mailing_model_id.model == 'mailing.list' else mailing.mailing_model_id.model

    def _parse_mailing_domain(self):
        self.ensure_one()
        try:
            mailing_domain = literal_eval(self.mailing_domain)
        except Exception:
            mailing_domain = [('id', 'in', [])]
        return mailing_domain

    def get_recipients(self):
        mailing_domain = self._parse_mailing_domain()
        res_ids = self.env[self.mailing_model_real].search(mailing_domain)
        return res_ids

    def get_whatsapp_api_marketing_configuration(self):
        """ get configration value of whatsapp API from settings"""
        instance_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp_marketing.instance_id')
        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp_marketing.token')
        if not instance_id:
            raise ValidationError('Please Enter Instance ID in Setting')
        if not token:
            raise ValidationError('Please Enter Token in Setting')
        print(instance_id)
        print(token)
        return instance_id, token

    def check_whatsapp_api_config(self):
        instance_id, token = self.get_whatsapp_api_marketing_configuration()

        url = f"https://api.ultramsg.com/{instance_id}/instance/status"

        querystring = {
            "token": token
        }

        headers = {'content-type': 'application/json'}
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Instance is Connected',
                    'type': 'rainbow_man',
                }
            }
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at ")
            raise ValidationError(_("A connection error occurred. Please check your internet connection."))

        except requests.exceptions.Timeout:
            _logger.exception("The request timed out. ")
            raise ValidationError(_("The request timed out."))

        except requests.exceptions.HTTPError as error:
            _logger.exception(
                "invalid API request at"
            )
            raise ValidationError(_("The communication with the API failed.\n %s" % error))
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            _logger.exception(
                "An error occurred"
            )
            raise ValidationError(_("An error occurred.\n %s" % e))

        print(response.text)
        print(response.json())
        if response.json().get('error'):
            raise ValidationError(response.json()['error'])

    def get_whatsapp_list_contact(self):
        whatsapp_list_contact = []
        for rec in self.whatsapp_list:
            data = [r.partner_id.id for r in rec.whatsapp_line_ids]
            whatsapp_list_contact += data

        return self.env['res.partner'].search([('id', 'in', list(set(whatsapp_list_contact)))])


    def send_ultramsg_func(self):




        self.check_whatsapp_api_config()
        instance_id, token = self.get_whatsapp_api_marketing_configuration()
        partner_ids = self.get_recipients() if self.mailing_model_name != 'mailing.list' else self.get_whatsapp_list_contact()
        print('partner',partner_ids)
        print('get_recipients',self.get_recipients())
        if len(partner_ids) < 1:
            raise UserError(_('There are no Clients Selected'))
        client_list = []
        response_result=''
        for partner in partner_ids:
            if self.attachment_ids:
                for attachment in self.attachment_ids:
                    ff = attachment.datas
                    url = f"https://api.ultramsg.com/{instance_id}/messages/document"
                    payload = json.dumps({
                        "token": token,
                        "to": partner.phone or partner.mobile,
                        "filename": attachment.name,
                        "document": ff.decode('utf-8'),
                        "caption": attachment.description or '',
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    try:
                        response = requests.request("POST", url, headers=headers, data=payload)
                        response_result = response
                        response.raise_for_status()
                    except requests.exceptions.ConnectionError:
                        _logger.exception("unable to reach endpoint at ")
                        raise ValidationError(_("A connection error occurred. Please check your internet connection."))
                    except requests.exceptions.Timeout:
                        _logger.exception("The request timed out. ")
                        raise ValidationError(_("The request timed out."))
                    except requests.exceptions.HTTPError as error:
                        _logger.exception(
                            "invalid API request at"
                        )
                        raise ValidationError(_("The communication with the API failed.\n %s" % error))
                    except requests.exceptions.RequestException as e:
                        print("An error occurred:", e)
                        _logger.exception(
                            "An error occurred"
                        )
                        raise ValidationError(_("An error occurred.\n %s" % e))


            else:
                url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
                payload = json.dumps({
                    "token": token,
                    "to": partner.phone or partner.mobile,
                    "body": self.message or ''
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                try:
                    response = requests.request("POST", url, headers=headers, data=payload)
                    response_result = response
                    response.raise_for_status()
                except requests.exceptions.ConnectionError:
                    _logger.exception("unable to reach endpoint at ")
                    raise ValidationError(_("A connection error occurred. Please check your internet connection."))
                except requests.exceptions.Timeout:
                    _logger.exception("The request timed out. ")
                    raise ValidationError(_("The request timed out."))
                except requests.exceptions.HTTPError as error:
                    _logger.exception(
                        "invalid API request at"
                    )
                    raise ValidationError(_("The communication with the API failed.\n %s" % error))
                except requests.exceptions.RequestException as e:
                    print("An error occurred:", e)
                    _logger.exception(
                        "An error occurred"
                    )
                    raise ValidationError(_("An error occurred.\n %s" % e))

            data = {
                'name': self.id,
                'partner_id': partner.id,
                'phone': partner.phone or partner.mobile,
                'state_description': response_result.json().get('error') if response_result.json().get('error') else response_result.json().get('sent') ,
                'state': 'failure' if response_result.json().get('error') else 'sent',
            }

            client_list.append(data)
        self.env['whatsapp.marketing.line'].create(client_list)

        self.state = 'done'


    def make_request_and_handel(self,request_info):
        """make request using requests module and handel exception """
        try:
            response = request_info
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at ")
            raise ValidationError( _("A connection error occurred. Please check your internet connection."))
        except requests.exceptions.Timeout:
            _logger.exception("The request timed out. ")
            raise ValidationError(_("The request timed out."))
        except requests.exceptions.HTTPError as error:
            _logger.exception(
                "invalid API request at"
            )
            raise ValidationError(_("The communication with the API failed.\n %s" % error))
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            _logger.exception(
                "An error occurred"
            )
            raise ValidationError(_("An error occurred.\n %s" % e))



    def action_confirm(self):
        """convert state from draft to confirm"""
        self.state = 'confirm'

    def action_cancel(self):
        """convert state from confirm to cancel"""
        self.state = 'cancel'

    def action_reset_to_draft(self):
        """convert state from cancel to draft"""
        self.state = 'draft'

    def action_view_mailing_contacts(self):
        """Show the mailing contacts who are in a mailing list selected for this mailing."""
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mass_mailing.action_view_mass_mailing_contacts')
        if self.contact_list_ids:
            action['context'] = {
                'default_mailing_list_ids': self.contact_list_ids[0].ids,
                'default_subscription_list_ids': [(0, 0, {'list_id': self.contact_list_ids[0].id})],
            }
        action['domain'] = [('list_ids', 'in', self.contact_list_ids.ids)]
        return action



    # smart button
    def action_open_sent_message(self):
        return {
            'name': _('Sent'),
            'res_model': 'whatsapp.marketing.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('name.id', '=', self.id),('state', '=', 'sent')],
        }

    def action_open_failure_message(self):
        return {
            'name': _('Failure'),
            'res_model': 'whatsapp.marketing.line',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('name.id', '=', self.id), ('state', '=', 'failure')],
        }

    def sent_message_count_func(self):
        for rec in self:
            sent_message = self.env['whatsapp.marketing.line'].search_count(
                [('name.id', '=', rec.id), ('state', '=', 'sent'), ])
            rec.sent_message_count = sent_message if sent_message else 0

    def failure_message_count_func(self):
        for rec in self:
            failure_message = self.env['whatsapp.marketing.line'].search_count(
                [('name.id', '=', rec.id), ('state', '=', 'failure'), ])
            rec.failure_message_count = failure_message if failure_message else 0



    # schedule messages
    def _process_whatsapp_marketing_queue(self):
        self.send_ultramsg_func()
        self.state = 'done'
        # self.ir_cron_id.sudo().unlink()
        print( self.ir_cron_id.id,'ppppp')
        print(self.ir_cron_id.active)
        print(self.ir_cron_id.state)
        # ss=self.env['ir.cron'].browse(self.ir_cron_id.id).active=False
        # print(ss.active)
        # print(ss.code)
        # query = "UPDATE ir_cron SET active = False WHERE id =%s" %self.ir_cron_id.id
        # print(query)
        # tt=self._cr.execute(query)
        # print(tt)
        print('ooooooooooosssssssssss')

    def action_schedule(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "whatsapp_marketing.whatsapp_marketing_schedule_date_action")
        action['context'] = dict(self.env.context, default_whatsapp_marketing_id=self.id, dialog_size='medium')
        return action

