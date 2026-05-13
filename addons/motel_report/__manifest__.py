{
    "name": "Motel Report",
    "version": "17.0.1.0.1",
    "summary": "Dashboard and reporting for motel management",
    "category": "Hospitality",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": [
        "motel_base",
        "motel_security",
        "motel_room",
        "motel_booking",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/dashboard.xml",
        "views/motel_dashboard_views.xml",
        "views/motel_report_menus.xml",
    ],
    "application": False,
    "installable": True,
}
