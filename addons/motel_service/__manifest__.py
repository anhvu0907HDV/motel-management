{
    "name": "Motel Service",
    "version": "17.0.1.0.1",
    "summary": "Base module for motel management",
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
        "data/sequence.xml",
        "views/motel_service_views.xml",
        "views/motel_service_menus.xml",
    ],
    "application": False,
    "installable": True,
}
