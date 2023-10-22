from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    instance_id = fields.Char(string="Whatsapp Instance ID", config_parameter='whatsapp_marketing.instance_id')
    token = fields.Char(string="Whatsapp Token", config_parameter='whatsapp_marketing.token')
