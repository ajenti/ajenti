[![Logo](../docs/img/Logo.png)](https://ajenti.org/)

----

# Setup development environment

- I. Install Ajenti, build tools and start the backend
- II. Setup plugin environment

## I. Install Ajenti, build tools and start the backend

See the page
https://docs.ajenti.org/en/latest/dev/setup-devenv-extension-plugins.html
## II. Automated Startup

### Run the services

This utility provides a convenient way to manage Yarn processes for Ajenti plugins.
Use the provided script to manage Yarn processes in bulk. 
This option is best if you're looking to save time and automate the routine start-up and shutdown 
of multiple Yarn instances associated with Ajenti plugins.

#### Initial setup:

open the  `setupFrontend.sh` adjust the plugins list you want to use.<br><br>
`./setupFrontend.sh` link - Builds the core library ngx-ajenti, makes setup of all selected plugins.<br><br>
While developement:<br>
`./setupFrontend.sh start` - Starts the core pluginshell + all selected plugins.<br>

`./setupFrontend.sh kill` - Stops all started plugin<br><br>
`./setupFrontend.sh restart` - Stops all started plugin and starts them again


## III. Setup plugin environment

To setup the plugin development is required

- build `ngx-ajenti` plugin
- build and run the `shell` plugin
- build and run each plugin you are working on

### Build the ngx-ajenti plugin

1. `cd plugins-new/ngx-ajenti`
2. `yarn install`
3. `yarn run build`

### Setup of one plugin

The following steps are for one plugin. Each plugin is an Angular application. To run multiple plugins at once, repeat the steps for each plugin.
(Replace the placeholder `{PLUGIN_NAME}`with the name of your plugin.)

1. `cd {PLUGIN_NAME}/frontend`
2. Set yarn as default package manager
   `ng config -g cli.packageManager yarn`
3. run `yarn install` to install all required dependencies.
4. create link to ngx-ajenti library `ln -nsf ../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core`
5. copy `proxy.conf.template.json` to `proxy.conf.json`
6. (Optional) Update the `localhost` in the`proxy.conf.json` if Ajenti runs on a different machine than is accessed on.
7. (Optional) If running multiple plugins make sure the port in the `angular.json` (` "port": 4200,`) is unique.

### Run the plugin(Application)

(Use new terminal window for each plugin.)

1. `cd plugins-new/{PLUGIN_NAME/frontend)`
2. run `yarn start`.  
   (Optional) Rebuild on code changes:   
   `yarn start --watch`  
   (Optional) To use your developer machine's host:   
   `yarn start -- --host my-host-name --disable-host-check` => This is very useful for testing on mobile devices!
3. The application is now available on the http://localhost:4200 ( the port is defined in the `angular.json`)


