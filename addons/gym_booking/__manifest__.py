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
        'data/gym_config_data.xml',
        'data/cron.xml',
        'views/gym_activity_views.xml',
        'views/gym_schedule_views.xml',
        'views/gym_booking_batch_views.xml',
        'views/gym_booking_views.xml',
        'views/gym_member_views.xml',
        'views/gym_subscription_views.xml',
        'views/gym_config_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/gym_activity_demo.xml',
        'demo/gym_schedule_demo.xml',
        'demo/gym_member_demo.xml',
        'demo/gym_subscription_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}