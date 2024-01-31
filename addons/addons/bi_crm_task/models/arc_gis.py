# models/arcgis_integration.py
from odoo import models, fields, api
import requests
from arcgis.gis import GIS

class ArcGISIntegration(models.Model):
    _name = 'arcgis.integration'
    _description = 'ArcGIS Integration'

    name = fields.Char(string='Name')
    arcgis_username = fields.Char(string='ArcGIS Username')
    arcgis_password = fields.Char(string='ArcGIS Password')
    map_html = fields.Html(string='Map HTML', compute='_compute_map_html', readonly=True, sanitize=False)
    survey_html = fields.Html(string='Survey HTML', compute='_compute_survey_html', readonly=True, sanitize=False)

    @api.depends('name', 'arcgis_username', 'arcgis_password')
    def _compute_survey_html(self):
       self.survey_html = f'<iframe name="survey123webform" width="500" height="400" frameborder="0" marginheight="0" marginwidth="0" title="My Survey" src="https://survey123.arcgis.com/share/050e468afd75464ba6e8079b0bc34c1c" allow="geolocation https://survey123.arcgis.com; camera https://survey123.arcgis.com"></iframe>'
    @api.depends('name', 'arcgis_username', 'arcgis_password')
    def _compute_map_html(self):
        # Replace 'YourWebMapID' with the actual ID of your web map
        webmap_id = '9d44eb41a63242b0998379c416fb504d'
        
        # Use the ArcGIS API to generate a token for authentication
        token_url = 'https://www.arcgis.com/sharing/rest/generateToken?'
        arcgis_username = "SolutionsAnalyst"
        arcgis_password = "SolutionsAnalyst@1234"
        token_params = {
            'f': 'json',
            'username': arcgis_username,
            'password': arcgis_password,
            'referer': 'https://strategizeit.maps.arcgis.com/home/webmap/viewer.html?webmap=9d44eb41a63242b0998379c416fb504d'
        }

        # Make a request to obtain the token
        token_response = requests.post(token_url, data=token_params )
        token_data = token_response.json()
        
        # Check if the token was obtained successfully
        if 'token' in token_data:
            # Generate HTML for the ArcGIS map within an iframe with the obtained token
            map_html = f'<iframe width="100%" height="600" src="//strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=9d44eb41a63242b0998379c416fb504d&extent=33.0647,30.9706,33.2671,31.0619&home=true&zoom=true&previewImage=false&scale=true&search=true&searchextent=true&details=true&legendlayers=true&active_panel=details&basemap_gallery=true&disable_scroll=true&theme=light&access_token={token_data["token"]}"></iframe>'
          #  map_html = f'<iframe width="100%" height="600" src="https://strategizeit.maps.arcgis.com/home/webmap/viewer.html?webmap=9d44eb41a63242b0998379c416fb504d&token={token_data["token"]}"></iframe>'
        else:
            # If token retrieval fails, use a message or a different approach
            #map_html = f'<iframe width="100%" height="600" src="//strategizeit.maps.arcgis.com/apps/Embed/index.html?webmap=9d44eb41a63242b0998379c416fb504d&extent=33.0315,30.9573,33.2338,31.0487&zoom=true&previewImage=true&scale=true&disable_scroll=true&theme=light&token=Qo4u8tBvwdY5kPU3H12YJYkAaJTRAT3M6C0U-eWKgz1OTlKItF1XcoBU-mKbNtlx9t5_7zxMb1EXJj2QsQPTdX2V3pYnyrpTmxAaXdHp7Qrz5m6GaRlgQS0wMn87b-CljS6HPPUwZhQP-SDO-2WTU84C9WUMyvbdjtMFpVKABlmN46KXhaIGP0gN0WE_QzYBqoqFKCAECqvEqX3K49Dt1Rn2kdCLOJOc3t5pnuJ_VlX5KtO4VpnIluIxaiXBJ8PtOGmqp97INiYKxOBJjW-gkK2IBG-5FqIpQKvQ63S3zEc." frameborder="0" allowfullscreen></iframe>'

            map_html = '<p>Error: Unable to obtain ArcGIS token.</p>'

        # Save the generated HTML to the model
        self.map_html = map_html
