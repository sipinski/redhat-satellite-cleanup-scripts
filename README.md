# redhat-satellite-cleanup-scripts
A quick and dirty python script that can be used to cleanup duplicate content host registrations in Redhat Satellite 6, caused by multiple automated OS installations and registrations via kickstart. 

The script connects to satellites postgres foreman database to get a list of duplicate system names and their UUIDs, then uses Satellite's hammer tool to remove the systems. To avoid hammer from prompting you for satellite credentials, be sure to configure your password ~/.hammer/cli_config.yml

:foreman:
    :enable_module: true
    :host: 'https://localhost/'
    :username: 'username'
    :password: 'password'
