# -*- coding: utf-8 -*-
{
    'name': "Whatsapp Marketing With Odoo",

    'summary': """
    Integrate whatsapp with odoo for marketing
        """,

    'description': """
    Integrate whatsapp with odoo for marketing (ultramsg API Provider)
    """,

    'author': "Technolgy Resouoces Planning group",
    'website': "https://trp.sa/",

    'category': 'Marketing/Whatsapp Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'mass_mailing'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_marketing.xml',
        'views/whatsapp_marketing_line.xml',
        'views/mailing_contract.xml',
        'views/whatsapp_list.xml',
        'views/rec_config_settings.xml',
        'data/ir_corn_data.xml',
        'wizard/whatsapp_marketing_schedule_date_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 30.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
