# -*- coding: utf-8 -*-
# from odoo import http


# class WhatsappMarketing(http.Controller):
#     @http.route('/whatsapp_marketing/whatsapp_marketing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/whatsapp_marketing/whatsapp_marketing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('whatsapp_marketing.listing', {
#             'root': '/whatsapp_marketing/whatsapp_marketing',
#             'objects': http.request.env['whatsapp_marketing.whatsapp_marketing'].search([]),
#         })

#     @http.route('/whatsapp_marketing/whatsapp_marketing/objects/<model("whatsapp_marketing.whatsapp_marketing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('whatsapp_marketing.object', {
#             'object': obj
#         })
