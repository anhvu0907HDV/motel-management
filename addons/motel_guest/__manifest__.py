{
    "name": "Motel Guest",
    "version": "17.0.1.0.1",
    "summary": "Guest management module for motel management",
    "category": "Hospitality",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": [
        "motel_base",
        "motel_security",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/motel_guest_views.xml",
        "views/motel_guest_menus.xml",
    ],
    "application": False,
    "installable": True,
}
