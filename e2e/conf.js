require('coffee-script');

exports.config = {
    seleniumAddress: 'http://localhost:4444/wd/hub',
    specs: ['spec.coffee'],
    onPrepare: function() {
        global.By = global.by;  
        global.takeScreenshot = function () {
            browser.takeScreenshot.then(function (data) {
                fs.writeFile('screen.png', data, 'binary');
            });
        }
    },
};
