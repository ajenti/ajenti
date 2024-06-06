const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const mf = require('@angular-architects/module-federation/webpack');
const path = require('path');
const share = mf.share;

const sharedMappings = new mf.SharedMappings();
sharedMappings.register(
  path.join(__dirname, 'tsconfig.json'),
  [/* mapped paths to share */],
);

module.exports = {
  output: {
    uniqueName: 'session_list',
    publicPath: 'auto',
    devtoolNamespace: 'session_list',
    scriptType: 'text/javascript',
  },
  optimization: {
    // Only needed to bypass a temporary bug
    runtimeChunk: false,
  },
  resolve: {
    alias: {
      ...sharedMappings.getAliases(),
    },
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'session_list',
      filename: 'remoteEntry.js',
      exposes: {
        './Module': './src/app/session_list/session_list.module.ts',
      },
      shared: share({
        '@ajenti/*': {singleton: true},
        '@angular/animations': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/router': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/core': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/common': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/material': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/platform-browser': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/platform-browser/animations': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/common/http': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@ngx-ajenti/core': {singleton: true, strictVersion: false},
        '@ngx-loading-bar/core': {singleton: true, strictVersion: false, requiredVersion: 'auto'},
        '@ngx-loading-bar/http-client': {singleton: true, strictVersion: false, requiredVersion: 'auto'},
        'rxjs': {singleton: true, strictVersion: true, requiredVersion: 'auto'},

        ...sharedMappings.getDescriptors(),
      }),
    }),
    sharedMappings.getPlugin(),
  ],
};
