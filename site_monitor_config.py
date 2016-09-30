#!/usr/bin/python3

config = {
	'sites': [
		{	# Reference Site, to review if there a internet access
			'reference': True,
			'name': 'Google',
			'host': 'google.com', 
			'url': 'https://www.google.com', 
			'timeout': 10
		},
		{	# Template Site
			'enabled': True,
			'name': 'Google',
			'host': 'google.com', 
			'url': 'https://www.google.com', 
			'timeout': 10,
			'notify': ['']
		}
	],
	'smtp': {
		'server': '',
		'port': 0,
		'login': {'user': '', 'password': ''},
		'from_address': ''
	},
	'global': {
		'notify': []
	}
}
