template = {
    "swagger": "2.0",
    "info": {
        "version": "1.0.0",
        "title": "Bookmarks API",
        "description": "API to manage Bookmarks",
        "termsOfService": "http://swagger.io/terms/",
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
        },
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "dev@mailinator.com",
            "url": "http://www.example.com",
        },
    },
    "basePath": "/api/v1",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
        }
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda rule: True,
        },
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/",
}
