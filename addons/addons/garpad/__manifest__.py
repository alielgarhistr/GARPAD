# __manifest__.py

{
    'name': 'GARPAD PROCESS',
    'version': '17.0',
    'author': 'Ali Elgarhi',
    'depends': ['base', 'account', 'sale', 'website'],
    'application': True,
    'website': True,
    'category': 'Services',
    'data': [
        'views/garpad_request.xml',
        #'security/ir.model.access.csv',
    ],
}
