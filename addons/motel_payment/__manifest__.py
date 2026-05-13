{
    "name": "Motel Payment",
    "version": "17.0.1.0.3",
    "summary": "Payment module for motel management",
    "category": "Hospitality",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": [
        "motel_base",
        "motel_security",
        "motel_booking",
        "mail",
    ],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "views/motel_payment_views.xml",
        "views/motel_payment_menus.xml",
    ],
    "application": False,
    "installable": True,
}
