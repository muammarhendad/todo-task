import datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TodoTask(models.Model):
    _name = 'todo.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Task'

    name = fields.Char('Task Name')
    due_date = fields.Date()
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('closed', 'closed'),
    ], default='new', tracking=1)
    assign_to_id = fields.Many2one('res.partner')
    description = fields.Text()
    estimated_time = fields.Float(digits=(0, 2))
    line_ids = fields.One2many('todo.task.line', 'todo_task_id')
    total_hours = fields.Float(compute='_compute_total')
    active = fields.Boolean(default=True)
    is_late = fields.Boolean(readonly=True)

    @api.depends('line_ids')
    def _compute_total(self):
        for rec in self:
            total = 0.0
            for line in rec.line_ids:
                total += line.times
            rec.total_hours = total
            if rec.total_hours > rec.estimated_time:
                raise ValidationError('total of hours more than estimated time !!')

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_new(self):
        for rec in self:
            rec.state = 'new'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'

    def action_closed(self):
        for rec in self:
            # rec.state = 'closed'
            rec.write({
                'state': 'closed'
            })

    def check_due_date(self):  # self here not records but model (todo.task)
        tasks_ids = self.search([])
        for rec in tasks_ids:
            print(rec)
            if rec.due_date and rec.due_date < fields.date.today() and rec.state != 'completed':
                rec.is_late = True
            else:
                rec.is_late = False


class TodoTaskLine(models.Model):
    _name = "todo.task.line"

    todo_task_id = fields.Many2one('todo.task')
    times = fields.Float('Times In Hours', digits=(0, 2))
    task_date = fields.Date(default=datetime.date.today())
    description = fields.Text()
