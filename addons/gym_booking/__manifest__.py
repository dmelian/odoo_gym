{
    'name': 'Gym Booking',
    'version': '18.0.1.0.0',
    'summary': 'Gestión de reservas para gimnasios',
    'author': 'Domingo Melián',
    'category': 'Services',
    'depends': ['base', 'mail'], 
    # ponemos mail por el chatter - para tener el historial de cambios en las reservas
    # también pondremos website cuando haga falta.
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/gym_activity_views.xml',
        'views/gym_schedule_views.xml',
        'views/gym_booking_views.xml',
        'views/gym_member_views.xml',
        'views/gym_subscription_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}