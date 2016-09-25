# Site Monitor v0.0.1

Yet Another Site Monitor

The intention of this tool is provide a simple way to monitor your site, but at the same time highly configurable.

----------

##Technical considerations

This tools should run with Python 3

##Configurations and use

Consider take a look and configure the the file **site_monitor_config.py**

Inside the **sites** array are a specific configuration

```python
{	# Reference Site, to review if there a internet access
	'reference': True,
	'name': 'Google',
	'host': 'google.com', 
	'url': 'https://www.google.com', 
	'timeout': 10
},
```
This site is to ensure that the script has access to internet, if you like to test with another site feel free to change it.
To work this site need to has the **'reference'** key to **True**

Under the same **sites** array you should include your sites to be monitoring:

```python
{	# Template Site
	'enabled': True,
	'name': 'Site Name',
	'host': 'site.com', 
	'url': 'https://www.site.com', 
	'timeout': 10,
	'notify': ['email@site.com']
}
```
The **notify** array should contains the email addresses to be notified

And the **smtp** configuration:
```python
'smtp': {
	'server': '',
	'port': 0,
	'login': {'user': '', 'password': ''},
	'from_address': ''
}
```
This section should be configured and verified to send the notifications

## How to Run

Just execute the file **site_monitor.py**

##LICENSE
GPL v3
