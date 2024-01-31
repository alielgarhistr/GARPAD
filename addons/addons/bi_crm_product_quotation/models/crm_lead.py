# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CopyRights(models.Model):
    _name = 'copy.rights'
    _description = "Copy Rights"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _order = 'create_date desc'

    name= fields.Char(string="اسم الطلب")
    crm_desc = fields.Html(string="الوصف")
    lead_line_id = fields.Many2one('garpad.request',string ="الطلب")
    partner_id = fields.Many2one('res.partner', string='اسم الطالب',required=True)
    currency_id = fields.Many2one('res.currency', string='العملة')
    map_html = fields.Html(string='Map HTML', readonly=True, sanitize=False)
    credit = fields.Monetary(related='partner_id.credit',string ="الرصيد")
    debit = fields.Monetary(related='partner_id.debit',string ="المديونية")
    total_invoiced = fields.Monetary(related='partner_id.total_invoiced',string ="المبلغ المدفوع")
    sale_order_count = fields.Integer(related='partner_id.sale_order_count',string ="طلبات الدفع")
    opportunity_count = fields.Integer(related='partner_id.opportunity_count',string ="طلبات الخدمة")
    total_due= fields.Monetary(related='partner_id.total_due',string ="المبلغ المستحق")
    service_type = fields.Many2one(related='lead_line_id.service_type',string ="نوع الخدمة")
    land_number = fields.Char(string='رقم قطعة الارض',required=True)
    request_status_id = fields.Many2one('garpad.request.status', related='lead_line_id.status_id', string='مرحلة الطلب')
    invoice_id = fields.Many2one('account.move', string='الفاتورة')
    payment_status = fields.Selection([
        ('not_paid', 'غير مدفوع'),
        ('paid', 'مدفوع'),
    ], string='حالة الفاتورة', related='invoice_id.payment_state', readonly=True)
    status = fields.Selection([
        ('draft', 'جديد'),
        ('progress', 'جاري'),
        ('confirmed', 'تم'),
        ('cancelled', 'ملغي'),
         ], string='حالة الطلب', default='draft')
     #suvery form fields#
    ycoordinate = fields.Char(string='Y Coordinate')
    xcoordinate = fields.Char(string='X Coordinate')
    description = fields.Char(string='الوصف')
    statussurv = fields.Char(string='الحالة')
    notes = fields.Text(string='ملاحظات')
    parcel_code = fields.Char(string='رقم القطعة')
    observer = fields.Char(string='القائم بالمعاينة')
    #end suvery form fields#

    def set_status_cancel(self):
        for record in self:
            record.write({'status': 'cancelled'})

    def set_status_done(self):

        for record in self:
            request = self.env['garpad.request'].search([('id','=',record.lead_line_id.id)])
            request.write({'status_id': 130})
            RequestPrice = self.env['request.price'].search([('lead_line_id','=',record.lead_line_id.id)])
            if RequestPrice:
                RequestPrice.write({'status': 'progress'})
            else:   
                RequestPrice = self.env['request.price'].create({
                    'crm_desc': record.crm_desc,
                    'name': record.name,
                    'lead_line_id': record.lead_line_id.id,
                    'partner_id': record.partner_id.id,
                    'map_html': record.map_html,
                    'currency_id': record.currency_id.id,
                    'land_number': record.land_number,
                    #'request_status_id': record.request_status_id.id,
                    'service_type': record.service_type.id,
                    'status': 'draft',
                    'xcoordinate': record.xcoordinate,
                    'ycoordinate': record.ycoordinate,
                    'description': record.description,
                    'statussurv': record.statussurv,
                    'notes': record.notes,
                    'parcel_code': record.parcel_code,
                    'observer': record.observer,
                    'message_ids': [(0, 0, {
                         'body': self.description,
                         'attachment_ids': [(6, 0, self.message_ids.attachment_ids.ids)],
                            'author_id': self.partner_id.id,
                             'res_id': self.id,
                         'model': 'request.price',
              
                                })],

                })
                attachment_ids = self.env['ir.attachment'].search([('res_model', '=', 'copy.rights'),('res_id', '=', self.id),])
                create_id = self.env['request.price'].search([('lead_line_id', '=', self.lead_line_id.id)], limit=1)
                for attachment in attachment_ids:
                   attachment.copy(default={'res_model': 'request.price', 'res_id': create_id.id})
        #self.env['request.price'].create(RequestPrice) 
        
            record.write({'status': 'confirmed'})
            

           



class RequestPrice(models.Model):
    _name = 'request.price'
    _description = "Request Price"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _order = 'create_date desc'

    name= fields.Char(string="اسم الطلب")
    request_product_ids = fields.One2many('request.line', 'request_line_id', string='البنود', copy=True)
    crm_desc = fields.Html(string="Request Description")
    lead_line_id = fields.Many2one('garpad.request',string ="الطلب")
    status = fields.Selection([
        ('draft', 'جديد'),
        ('progress', 'جاري'),
        ('confirmed', 'تم'),
        ('cancelled', 'ملغي'),
         ], string='حالة الطلب', default='draft')
    partner_id = fields.Many2one('res.partner', string='اسم الطالب',required=True)
    currency_id = fields.Many2one('res.currency', string='العملة')
    map_html = fields.Html(string='Map HTML', readonly=True, sanitize=False)
    credit = fields.Monetary(related='partner_id.credit',string ="الرصيد")
    debit = fields.Monetary(related='partner_id.debit',string ="المديونية")
    total_invoiced = fields.Monetary(related='partner_id.total_invoiced',string ="المبلغ المدفوع")
    sale_order_count = fields.Integer(related='partner_id.sale_order_count',string ="طلبات الدفع")
    opportunity_count = fields.Integer(related='partner_id.opportunity_count',string ="طلبات الخدمة")
    total_due= fields.Monetary(related='partner_id.total_due',string ="المبلغ المستحق")
    service_type = fields.Many2one(related='lead_line_id.service_type',string ="نوع الخدمة")
    land_number = fields.Char(string='رقم قطعة الارض',required=True)
    request_status_id = fields.Many2one('garpad.request.status', related='lead_line_id.status_id', string='مرحلة الطلب')
    invoice_id = fields.Many2one('account.move', string='الفاتورة')
    payment_status = fields.Selection([
        ('not_paid', 'غير مدفوع'),
        ('paid', 'مدفوع'),
    ], string='حالة الفاتورة', related='invoice_id.payment_state', readonly=True)
      #suvery form fields#
    ycoordinate = fields.Char(string='Y Coordinate')
    xcoordinate = fields.Char(string='X Coordinate')
    description = fields.Char(string='الوصف')
    statussurv = fields.Char(string='الحالة')
    notes = fields.Text(string='ملاحظات')
    parcel_code = fields.Char(string='رقم القطعة')
    observer = fields.Char(string='القائم بالمعاينة')
    #end suvery form fields#
    def set_status_cancel(self):
        for record in self:
            record.write({'status': 'cancelled'})

    def set_status_done(self):
        
        for record in self:
          record.write({'status': 'confirmed'})
        # create sale order from request price
        order_line = []
        for record in self.request_product_ids:
            order_line.append((0, 0, {
                'product_id': record.product_id.id,
                'name': record.name,
                'product_uom_qty': record.product_uom_quantity,
                'price_unit': record.price_unit,
                'tax_id': [(6, 0, record.tax_id.ids)],
            }))
        sale_obj = self.env['sale.order']
        if self.partner_id:
                    for record in self.request_product_ids:
                        if record.product_id and record.name:
                            sale_create_obj = sale_obj.create({
                                'partner_id': self.partner_id.id,
                                #'opportunity_id': self.id,
                                'state': "draft",
                                'order_line': order_line,
                            })
                            sale_create_obj.action_confirm()
                            return {
                                'name': "Sale Order",
                                'type': 'ir.actions.act_window',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'res_model': 'sale.order',
                                'view_id': self.env.ref('sale.view_order_form').id,
                                'target': "new",
                                'res_id': sale_create_obj.id
                            }
                    else:
                        raise UserError('Enter the "Product" and "Description".')
        else:
                    raise UserError('Please select the "Customer".')
        lead_id = self.lead_line_id.id
           # Search for the related crm.lead record
        lead_record = self.env['request.garpad'].browse(lead_id)
        if lead_record:
                  lead_record.action_quotations_view()
                  lead_record.stage_id = 17



class crm_lead(models.Model):
    _inherit = 'crm.lead'

    lead_product_ids = fields.One2many('lead.line', 'lead_line_id', string='Products', copy=True)
    crm_count = fields.Integer(string="Quotation",compute="get_quotation_count")
    is_crm_quotation = fields.Boolean('Is CRM Quotation')
    land_number = fields.Char(string="رقم القطعة")

    def action_quotations_view(self):
        order_line = [] 
        for record in self.lead_product_ids:  
            order_line.append((0, 0, {
                                     'product_id'     : record.product_id.id,
                                     'name'           : record.name, 
                                     'product_uom_qty': record.product_uom_quantity,
                                     'price_unit'     : record.price_unit,
                                     'tax_id'        : [(6, 0, record.tax_id.ids)],
                                }))
        
        sale_obj = self.env['sale.order']
        if self.partner_id:
            for record in self.lead_product_ids:  
                if record.product_id and record.name:
                    sale_create_obj = sale_obj.create({
                                    'partner_id': self.partner_id.id,
                                    'opportunity_id': self.id,
                                    'state': "draft",
                                    'order_line': order_line,
                                    })
                    sale_create_obj.action_confirm()
                return {
                    'name': "Sale Order",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': self.env.ref('sale.view_order_form').id,
                    'target': "new",
                    'res_id': sale_create_obj.id
                }
            else:
                raise UserError('Enter the "Product" and "Description".')
        else:
            raise UserError('Please select the "Customer".')             



    def open_quotation_from_view_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('partner_id','=',self.partner_id.id),('opportunity_id','=',self.id)]
        return action


    def get_quotation_count(self):
        count = self.env['sale.order'].search_count([('partner_id','=',self.partner_id.id),('opportunity_id','=',self.id)])
        self.crm_count = count

    def request_price(self):
        crm_lead = self
        product_data = {
            'crm_desc': crm_lead.description,
            'name': crm_lead.name,
            'lead_line_id': crm_lead.id,

        }
        product = self.env['request.price'].create(product_data)
        for record in self:
            record.stage_id = 13
        
        
    def request_copyrights(self):
        crm_lead = self
        product_data = {
            'crm_desc': crm_lead.description,
            'name': crm_lead.name,
            'lead_line_id': crm_lead.id,

        }
        product = self.env['copy.rights'].create(product_data)
        for record in self:
            record.stage_id = 12

    def request_progress(self):

        for record in self:
            record.stage_id = 19
            
            garpad_request_values = {
            'name': self.partner_id.name,  # Set the appropriate name
            'user_id': 3,  # Assign the sale order user
            'service_type': self.x_studio_servicetype.id,
            'lead_id': self.id,
            'land_number': self.land_number,
            'partner_id': self.partner_id.id,  # Assign the sale order user
            #'created_date': fields.Datetime.now(),
            #'source_id': self.id,  # Set the source ID as the sale order ID
            'status_id': 128,  # Set the appropriate status model 
            #copy files in attachment messages
            'message_ids': [(0, 0, {
                #'body': self.description,
                'attachment_ids': [(6, 0, self.message_ids.attachment_ids.ids)],
                'author_id': self.user_id.partner_id.id,
                 'res_id': self.id,
                'model': 'garpad.request',
               
              
            })],
            

            # Add other field values as needed
        }
        
        self.env['garpad.request'].create(garpad_request_values) 
        attachment_ids = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'),('res_id', '=', self.id),])
        create_id = self.env['garpad.request'].search([('lead_id', '=', self.id)], limit=1)
        #create attachments
        for attachment in attachment_ids:
            attachment.copy(default={'res_model': 'garpad.request', 'res_id': create_id.id})
       
    def request_review(self):

        for record in self:
            record.stage_id = 18
           
    def get_land_piece_number(self):
        for record in self:
            if record.description and 'رقم قطعة الارض :' in record.description:
                # Find the position of the text
                index = record.description.find('رقم قطعة الارض :')
                # Extract the value after the text
                land_piece_number = record.description[index + len('رقم قطعة الارض :'):]
                return land_piece_number.strip()
           
            return None
          