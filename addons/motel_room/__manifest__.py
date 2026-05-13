{
    "name": "Motel Room",
    "version": "17.0.1.0.1",
    "summary": "Room management",
    "category": "Hospitality",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": [
        "motel_base",
        "motel_security",
        "mail",
    ],
    "assets": {
        "web.assets_backend": [
            "motel_room/static/src/scss/room_kanban.scss",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/motel_room_views.xml",
        "views/motel_room_type_views.xml",
        "views/motel_room_menus.xml",
    ],
    "application": True,
    "installable": True,
}
