fs = require 'fs'

plugins = [
    'core'
    'ace'
    'augeas'
    'filesystem'
    'notepad'
]

files = [
    'test-main.coffee'
]

for d in plugins
    console.info 'Scanning resources in', d
    files.push "../plugins/#{d}/resources/build/all.vendor.js"
    files.push "../plugins/#{d}/resources/build/all.js"

#files.push 'node_modules/angular-mocks/angular-mocks.js'
files.push 'test-extras.coffee'
files.push 'tests/**/*.coffee'

module.exports = (config) ->
    config.set({
        basePath: '',
        frameworks: ['mocha', 'sinon-chai', 'chai-as-promised'],
        files: files,
        exclude: [],
        preprocessors: {
            '../plugins/**/*.coffee': ['coverage'],
            '**/*.coffee': ['coffee'],
        },
        coffeePreprocessor: {
            options: {
                sourceMap: true
            }
        },
        reporters: [
            'progress',
            'coverage',
        ],
        port: 9876,
        colors: true,
        logLevel: config.LOG_INFO,
        #logLevel: config.LOG_DEBUG,
        autoWatch: false,
        browsers: ['PhantomJS'],
        singleRun: true
        coverageReporter:
            reporters: [
                {type: 'html', subdir: '.'}
                {type: 'text-summary', subdir: '.', file: 'coverage.txt'}
            ]
    })
