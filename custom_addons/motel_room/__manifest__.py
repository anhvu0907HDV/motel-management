{
    "name": "Motel Room",
    "version": "17.0.1.0.0",
    "summary": "Room management",
    "category": "Hospitality",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": [
        "motel_base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/motel_room_views.xml",
        "views/motel_room_type_views.xml",
        "views/motel_room_menus.xml",
    ],
    "application": True,
    "installable": True,
}