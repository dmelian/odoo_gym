from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class GymPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values['gym_booking_count'] = 0  # show_count=False, no importa el valor
        return values

    @http.route('/my/gym', type='http', auth='user', website=True)
    def gym_home(self, **kwargs):
        member = request.env['gym.member'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        _logger.warning("USER ID: %s", request.env.user.id)
        _logger.warning("MEMBER: %s", member)

        return request.render('gym_booking.portal_gym_home', {
            'member': member,
        })

    @http.route('/my/gym/schedule', type='http', auth='user', website=True)
    def gym_schedule(self, **kwargs):
        config = request.env['gym.config'].sudo().get_config()

        morning_slots = [config.morning_start + i for i in range(config.morning_hours)]
        afternoon_slots = [config.afternoon_start + i for i in range(config.afternoon_hours)]
        slots = morning_slots + afternoon_slots

        days = [('0','Lunes'),('1','Martes'),('2','Miércoles'),('3','Jueves'),('4','Viernes')]

        schedules = request.env['gym.schedule'].sudo().search([])

        member = request.env['gym.member'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        subscribed_schedule_ids = []
        if member:
            subs = request.env['gym.subscription.line'].sudo().search([
                ('member_id', '=', member.id)
            ])
            subscribed_schedule_ids = subs.mapped('schedule_id').ids

        grid = {}
        for slot in slots:
            grid[slot] = {}
            for day, _ in days:
                match = schedules.filtered(
                    lambda s, d=day, sl=slot: s.day_of_week == d and s.time_start == sl
                )
                grid[slot][day] = {
                    'schedule': match[0],
                    'subscribed': match[0].id in subscribed_schedule_ids,
                } if match else None

        return request.render('gym_booking.portal_gym_schedule', {
            'member': member,
            'days': days,
            'slots': slots,
            'grid': grid,
        })        