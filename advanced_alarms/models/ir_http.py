# -*- coding: utf-8 -*-
from odoo import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(Http, self).session_info()
        result['advanced_alarms_time_format'] = self.env['ir.config_parameter'].sudo().get_param('advanced_alarms.time_format_preference', 'system')
        return result
