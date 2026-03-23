{
    'name': 'Gym Management',
    'version': '17.0.1.0.0',
    'depends': [
        'base',
        'sale_subscription',   # ← Clave: heredamos suscripciones
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/gym_member_views.xml',
        'views/gym_subscription_views.xml',
    ],
}