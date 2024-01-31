from odoo import models, fields, api, exceptions
import requests
import re
from arcgis.gis import GIS

class GarpadRequest(models.Model):
    _name = 'garpad.request'
    _description = 'Garpad Requests'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _order = 'create_date desc'

    name = fields.Char(string='اسم ', required=True)
    lead_id = fields.Many2one('crm.lead', string='الطلب المقدم',required=True)
    land_number = fields.Char(string='رقم قطعة الارض',required=True)
    gov = fields.Char(string='المحافظة')
    map_html = fields.Html(string='Map HTML', compute='_compute_map_html', readonly=True, sanitize=False)  
    service_type = fields.Many2one('x_', string='نوع الطلب',required=True)
    partner_id = fields.Many2one('res.partner', string='اسم الطالب',required=True)
    user_id = fields.Many2one('res.users', string='مسند الي', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='تاريخ الانشاء', default=fields.Datetime.now)
    invoice_id = fields.Many2one('account.move', string='الفاتورة', compute='_compute_invoice_id')
    source_id = fields.Many2one('sale.order', string='رقم الطلب')
    payment_status = fields.Selection([
        ('not_paid', 'غير مدفوع'),
        ('paid', 'مدفوع'),
    ], string='حالة الفاتورة', related='invoice_id.payment_state', readonly=True)
    status_id = fields.Many2one('garpad.request.status', string='Status')
    result = fields.Char(string='النتيجة')
    #suvery form fields#
    ycoordinate = fields.Char(string='Y Coordinate')
    xcoordinate = fields.Char(string='X Coordinate')
    description = fields.Char(string='الوصف')
    statussurv = fields.Char(string='الحالة')
    notes = fields.Text(string='ملاحظات')
    parcel_code = fields.Char(string='رقم القطعة')
    observer = fields.Char(string='القائم بالمعاينة')
    #end suvery form fields#
    
    # Chatter compute='_compute_invoice_id'
    def is_frontend_multilang(self):
        # Your implementation here
        return True  # or False based on your logic
    def report_msaha(self):
        self.status_id = self.env['garpad.request.status'].search([('name', '=', 'تقرير المعاينة')], limit=1)
        
    def fetch_attributes_by_land_number(self):
        # Replace this URL with the actual URL of your feature layer
        feature_layer_url = "https://services3.arcgis.com/N0l9vjYH8GLn5HZh/arcgis/rest/services/survey123_dc42444fef0d42cc9f5f85ba9da53e5f/FeatureServer/0"

        # Get the phone number from the current record's partner
        land_number = str(self.land_number)

        # Define the query parameters
        params = {
            'where': f"field_8 = '{land_number}'",
            'outFields': '*',
            'returnGeometry': 'false',
            'f': 'json'
        }

        # Make an HTTP GET request to the feature layer
        response = requests.get(feature_layer_url + '/query', params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Process the attributes and create or update records in the Odoo model
            for feature in data['features']:
                attributes = feature['attributes']

                # Create or update records in the Odoo model based on retrieved attributes
                self.env['garpad.request'].search([('id', '=', self.id)], order='id DESC', limit=1).write({'statussurv': attributes.get('field_5', ''),'parcel_code': attributes.get('field_8', ''),'observer': attributes.get('Creator', ''),'notes': attributes.get('field_7', ''),'gov': attributes.get('field_2', '')}
                                                                                                         
                                                                                                          )

        else:
            print("Error:", response.status_code)
    @api.depends('payment_status')
    #message_ids = fields.One2many('mail.message', 'res_id', domain=lambda self: [('model', '=', 'garpad.request')])
    def compoute_paid(self):
        for record in self:
            if record.payment_status == "paid":
                record.status_id = self.env['garpad.request.status'].search([('name', '=', 'التحصيل')], limit=1)
    def compoute_msaha(self):
        for record in self:
                record.status_id = self.env['garpad.request.status'].search([('name', '=', 'اجراء المعاينة')], limit=1)
    def _compute_button_visibility(self):
        for record in self:
            # Implement your logic here to determine which buttons should be visible
            record.show_confirm1_button = record.stage_id.name == 'معاينة الأرض و الرفع المساحي'
            record.show_confirm2_button = record.stage_id.name == 'مذكرة تفصيلية'
            record.show_confirm3_button = record.stage_id.name == 'تحرير العقد'
            record.show_confirm4_button = record.stage_id.name == 'تسليم الارض'
            record.show_confirm5_button = record.stage_id.name == 'تم'
            record.show_confirm_button = record.stage_id.name == 'تسديد المبلغ المستحق'
            record.show_confirm_button6 = record.stage_id.name == 'تم السداد'
            # Add more conditions as needed

    # Additional fields to control button visibility
    show_confirm_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm1_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm2_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm3_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm4_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm5_button = fields.Boolean(compute='_compute_button_visibility')
    show_confirm6_button = fields.Boolean(compute='_compute_button_visibility')


    @api.depends('source_id')
    def _compute_invoice_id(self):
        for record in self:
           ordername = record.source_id.name
           invoices = self.env['account.move'].search([('invoice_origin', '=', ordername)], limit=1)
           record.invoice_id = invoices.id if invoices else False
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
    def approv_cust(self):    
        for record in self:
            record.status_id = 138
            record.result = 'تمت الموافقة'
    def reject_cust(self):    
        for record in self:
            record.status_id = 138
            record.result = 'تم الرفض'
    def request_report(self):    
        for record in self:
            record.status_id = 136
    def request_survey(self):
      #open link in browser
        for record in self:
            #record.stage_id = 14
            survey_url = 'https://arcg.is/1qXyme'
            return {
            'type': 'ir.actions.act_url',
            'url': survey_url,
            'target': 'new',
        }   
    def request_copyrights(self):
        request = self
        request_data = {
            'name': request.name,
            'lead_line_id': request.id,
            'land_number': request.land_number,
            'service_type': request.service_type.id,
            'partner_id': request.partner_id.id,
            #'request_status_id': request.status_id.id,
            'map_html': request.map_html,
            'xcoordinate': request.xcoordinate,
            'ycoordinate': request.ycoordinate,
            'parcel_code': request.parcel_code,
            'observer': request.observer,
            'notes': request.notes,
            'statussurv': request.statussurv,
            'description': request.description,
            'message_ids': [(0, 0, {
                'body': self.description,
                'attachment_ids': [(6, 0, self.message_ids.attachment_ids.ids)],
                'author_id': self.partner_id.id,
                'res_id': self.id,
                'model': 'copy.rights',
              
            })],
            
        }
        product = self.env['copy.rights'].create(request_data)
        attachment_ids = self.env['ir.attachment'].search([('res_model', '=', 'garpad.request'),('res_id', '=', self.id),])
        create_id = self.env['copy.rights'].search([('lead_line_id', '=', self.id)], limit=1)
        #create attachments
        for attachment in attachment_ids:
            attachment.copy(default={'res_model': 'copy.rights', 'res_id': create_id.id})
        for record in self:
            record.status_id = 129 
            
    @api.depends('land_number','lead_id')
    def _compute_map_html(self):   
        if self.land_number == 121:
            self.map_html =  f'<iframe width="100%" height="600" src="https://strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=e3b8a2bf9fa14aacb2897e792934e430&extent=33.0647,30.9706,33.2671,31.0619&home=true&zoom=true&previewImage=false&scale=true&search=true&searchextent=true&details=true&legendlayers=true&active_panel=details&basemap_gallery=true&disable_scroll=true&theme=light&access_token=v9RSGG9Oo0Q7R0u-u0DaW4ZrwBOIpgQ6FOMY00AciFiu1Sb2zYgT9eZRH8OJ-J2C2-5mZLTz9z3AtQeUw7PWQ9wqZbuNWx7VtOjgK6F7kx5oDHoeSZcKtHJllhjTRro_uqD4jlIlLOIyy_jZP4FE8RhusBiVm2B9JcGhCf9TLczncOsGwA9SQrJIg-WtRDty1s5vWoVGSOCkdbgvDjm3t0bCSafDBL0k_e61zV2FtBM8fqRN2pL_Mm2SVOpddBLOApd137bHTHuWmsXeQMsCSIokEskmemFs7ygVPJrFSEg."></iframe>'
        if self.land_number == 104:
            self.map_html =  f'<iframe width="100%" height="600" src="https://strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=d1771e76b49042109625670fea14d995&extent=33.0647,30.9706,33.2671,31.0619&home=true&zoom=true&previewImage=false&scale=true&search=true&searchextent=true&details=true&legendlayers=true&active_panel=details&basemap_gallery=true&disable_scroll=true&theme=light&access_token=v9RSGG9Oo0Q7R0u-u0DaW4ZrwBOIpgQ6FOMY00AciFiu1Sb2zYgT9eZRH8OJ-J2C2-5mZLTz9z3AtQeUw7PWQ9wqZbuNWx7VtOjgK6F7kx5oDHoeSZcKtHJllhjTRro_uqD4jlIlLOIyy_jZP4FE8RhusBiVm2B9JcGhCf9TLczncOsGwA9SQrJIg-WtRDty1s5vWoVGSOCkdbgvDjm3t0bCSafDBL0k_e61zV2FtBM8fqRN2pL_Mm2SVOpddBLOApd137bHTHuWmsXeQMsCSIokEskmemFs7ygVPJrFSEg."></iframe>'
        if self.land_number == 2:
            self.map_html =  f'<iframe width="100%" height="600" src="https://strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=31d7ee23864d4f9d8fb5df1e1b1b978c&extent=33.0647,30.9706,33.2671,31.0619&home=true&zoom=true&previewImage=false&scale=true&search=true&searchextent=true&details=true&legendlayers=true&active_panel=details&basemap_gallery=true&disable_scroll=true&theme=light&access_token=v9RSGG9Oo0Q7R0u-u0DaW4ZrwBOIpgQ6FOMY00AciFiu1Sb2zYgT9eZRH8OJ-J2C2-5mZLTz9z3AtQeUw7PWQ9wqZbuNWx7VtOjgK6F7kx5oDHoeSZcKtHJllhjTRro_uqD4jlIlLOIyy_jZP4FE8RhusBiVm2B9JcGhCf9TLczncOsGwA9SQrJIg-WtRDty1s5vWoVGSOCkdbgvDjm3t0bCSafDBL0k_e61zV2FtBM8fqRN2pL_Mm2SVOpddBLOApd137bHTHuWmsXeQMsCSIokEskmemFs7ygVPJrFSEg."></iframe>'
        else:
           self.map_html = f'<iframe width="100%" height="600" src="https://strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=9d44eb41a63242b0998379c416fb504d&extent=33.0647,30.9706,33.2671,31.0619&home=true&zoom=true&previewImage=false&scale=true&search=true&searchextent=true&details=true&legendlayers=true&active_panel=details&basemap_gallery=true&disable_scroll=true&theme=light&access_token=v9RSGG9Oo0Q7R0u-u0DaW4ZrwBOIpgQ6FOMY00AciFiu1Sb2zYgT9eZRH8OJ-J2C2-5mZLTz9z3AtQeUw7PWQ9wqZbuNWx7VtOjgK6F7kx5oDHoeSZcKtHJllhjTRro_uqD4jlIlLOIyy_jZP4FE8RhusBiVm2B9JcGhCf9TLczncOsGwA9SQrJIg-WtRDty1s5vWoVGSOCkdbgvDjm3t0bCSafDBL0k_e61zV2FtBM8fqRN2pL_Mm2SVOpddBLOApd137bHTHuWmsXeQMsCSIokEskmemFs7ygVPJrFSEg."></iframe>'


class GarpadRequestStatus(models.Model):
    _name = 'garpad.request.status'
    _description = 'Garpad Request Status'

    name = fields.Char(string='Status Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)




class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    lead_id = fields.Many2one('crm.lead', string='Lead')

    @api.model
    def create(self, values):
      
        try:
            # Call the original create method
            ticket = super(HelpdeskTicket,self).create(values)
            
            # Create lead data from ticket information
            lead_data = {
                'name': ticket.name,
                'x_studio_servicetype': 1,
                'partner_id': ticket.partner_id.id,
                'type': 'opportunity',
                'description': ticket.description,
                'message_ids': [(0, 0, {
                'body': ticket.description,
                'attachment_ids': [(6, 0, ticket.message_ids.attachment_ids.ids)],
                'author_id': self.partner_id.id,
                'res_id': ticket.id,
                'model': 'crm.lead',
              
            })],
                # Add other fields as needed
            }

            # Create the lead record
            
            lead_obj = self.env['crm.lead']
            lead_id = lead_obj.create(lead_data)

            # Set the lead_id on the ticket
            ticket.write({'lead_id': lead_id.id})

            return ticket

        except exceptions.ValidationError as e:
            # Handle validation errors if any
            raise exceptions.UserError(f"Validation error: {e.name}")
        except Exception as e:
            # Handle other exceptions
            raise exceptions.UserError(f"An error occurred: {e}")