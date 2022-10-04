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
    uniqueName: 'fstab',
    publicPath: 'auto',
    devtoolNamespace: 'fstab',
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
      name: 'fstab',
      filename: 'remoteEntry.js',
      exposes: {
        './Module': './src/app/fstab/fstab.module.ts',
      },
      shared: share({
        '@ajenti/*': {singleton: true},
        '@angular/router': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/core': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
        '@angular/common': {singleton: true, strictVersion: true, requiredVersion: 'auto'},
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
