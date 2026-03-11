# 🏋️ gym_booking — Odoo 18 Gym Booking Module

A fully functional Odoo 18 Community module for managing gym class bookings, member subscriptions, and automated weekly scheduling. Built as teaching material for vocational IT students learning about ERP development and web markup languages.

---

## ✨ Features

- **Activity management** — Define gym classes with name, description, and capacity
- **Weekly schedules** — Assign activities to specific days and time slots
- **Member management** — Track members, subscription status, and booking history
- **Subscription lines** — Link members to specific weekly schedules
- **Booking system** — Create and manage individual class bookings with state tracking (`confirmed`, `cancelled`, `attended`)
- **Batch booking** — Automated weekly booking generation via cron job or manual trigger
- **Business rules** — Enforced validations: 24h advance booking, capacity limits, no schedule overlaps, weekday consistency
- **Customer portal** — Members can view their bookings and weekly schedule at `/my/gym`
- **Calendar view** — Visual weekly calendar of bookings grouped by activity
- **Chatter & tracking** — Full audit trail on bookings and members via `mail.thread`

---

## 🗂️ Module Structure

```
addons/gym_booking/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── gym_activity.py
│   ├── gym_schedule.py
│   ├── gym_member.py
│   ├── gym_subscription.py
│   ├── gym_booking_batch.py
│   ├── gym_booking.py
│   └── gym_config.py
├── views/
│   ├── gym_activity_views.xml
│   ├── gym_schedule_views.xml
│   ├── gym_member_views.xml
│   ├── gym_subscription_views.xml
│   ├── gym_booking_batch_views.xml
│   ├── gym_booking_views.xml
│   ├── gym_config_views.xml
│   └── menu.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── sequences.xml
│   ├── gym_config_data.xml
│   └── cron.xml
├── demo/
│   ├── gym_activity_demo.xml
│   ├── gym_schedule_demo.xml
│   ├── gym_member_demo.xml
│   └── gym_subscription_demo.xml
├── controllers/
│   ├── __init__.py
│   └── portal.py
├── templates/
│   └── portal_templates.xml
└── static/src/img/
    └── gym.svg
```

---

## 📋 Menu Layout

```
Gym
├── Bookings
│   ├── All Bookings
│   └── Batch History
├── Members
│   ├── Members
│   └── Subscriptions
└── Configuration
    ├── Activities
    ├── Schedules
    └── General Settings
```

---

## 🐳 Quick Start with Docker

### Prerequisites

- Docker Desktop installed
- Git

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/dmelian/odoo_gym.git
cd odoo_gym
```

2. **Start the containers**

```bash
docker-compose up -d
```

3. **Open Odoo in your browser**

```
http://localhost
```

4. **Create a database** — use the Odoo database manager at `http://localhost/web/database/manager`

5. **Install the module** — go to *Apps*, search for `gym_booking`, and click *Install*

### docker-compose.yml

```yaml
version: '3.1'
services:
  web:
    image: odoo:18.0
    depends_on:
      - db
    ports:
      - "80:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

---

## 🎭 Demo Data

The module ships with demo data for quick testing:

| Entity | Records |
|--------|---------|
| Activities | Yoga, Spinning, Pilates, Zumba |
| Schedules | 8 time slots across the week |
| Members | Ana García, Carlos López, María Martínez, Juan Pérez, Laura Sánchez |
| Subscriptions | 10 member–schedule links |

> **Portal testing tip:** Demo member *Ana García* is linked to the `Mitchell Admin` user, so you can test the customer portal immediately after install.

---

## 🔧 Technical Notes

### Odoo 18 Compatibility

This module targets **Odoo 18 Community** and follows its conventions:

- Uses `<list>` views (not `<tree>` — removed in Odoo 18)
- Uses `invisible=` domain syntax (Odoo 17+ style)
- `ir.cron` records do not use `numbercall` (removed in Odoo 18)
- Portal templates use `portal_docs_entry` with `portal_common_category` xpath

### Key Business Rules (enforced via `@api.constrains`)

- Bookings require at least **24 hours** advance notice
- Booking day must match the schedule's day of the week
- Bookings cannot exceed the activity's **capacity**
- A member cannot have **overlapping** bookings at the same time slot

### Automated Booking Generation

A cron job runs weekly to auto-generate bookings for all active subscriptions. It can also be triggered manually from *Gym → Configuration → General Settings → Generate Bookings*.

---

## 🌐 Customer Portal

Members can access their gym area at `/my/gym` after logging in:

| Route | Description |
|-------|-------------|
| `/my/gym` | Dashboard — active subscriptions and quick links |
| `/my/gym/schedule` | Weekly schedule grid with navigation |
| `/my/gym/bookings` | Upcoming and past bookings, with cancellation (>24h) |

---

## 📦 Dependencies

```python
'depends': ['base', 'mail', 'portal']
```

No external Python packages required.

---

## 🎓 Educational Context

This module was developed as a teaching project for **vocational IT students** (Formación Profesional, Spain) studying web markup languages. It covers:

- Odoo module structure and manifest
- Python models, fields, and ORM methods
- XML views: list, form, kanban, and calendar
- QWeb templates for portal/website
- HTTP controllers and routing
- Security rules and access control

---

## 📄 License

This project is released for educational purposes. Feel free to use, fork, and adapt it for your own learning or teaching.

---

