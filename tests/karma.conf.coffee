YAML = require 'yamljs'

plugins = [
    'core'
    'ace'
    'filesystem'
    'notepad'
]

files = [
  'test-main.coffee'
]

for d in plugins
    console.info 'Scanning resources in', d
    cfg = YAML.load("../plugins/#{d}/plugin.yml")
    for res in cfg.resources
        if /.*(js|coffee)$/.test(res)
            files.push "../plugins/#{d}/#{res}"

files.push 'node_modules/angular-mocks/angular-mocks.js'
files.push 'test-extras.coffee'
files.push 'tests/**/*.coffee'


module.exports = (config) ->
  config.set({
    basePath: '',
    frameworks: ['mocha', 'chai', 'sinon-chai', 'chai-as-promised'],
    files: files,
    exclude: [
    ],
    preprocessors: {
       '../plugins/**/*.coffee': ['coverage'],
       '**/*.coffee': ['coffee'],
    },
    coffeePreprocessor: {
      options: {
        sourceMap: true
      }
    },
    reporters: ['progress', 'coverage'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    #logLevel: config.LOG_DEBUG,
    autoWatch: false,
    browsers: ['PhantomJS'],
    singleRun: true
  })
