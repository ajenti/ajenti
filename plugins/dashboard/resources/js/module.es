angular.module('ajenti.dashboard', [
    'core',
]);

angular.module('ajenti.dashboard').run(customization => {
    customization.plugins.dashboard = {
        allowMove: true,
        allowRemove: true,
        allowConfigure: true,
        allowAdd: true,
        defaultConfig: {
            widgetsLeft: [
                {
                    id: 'w1',
                    typeId: 'hostname'

                },
                {
                    id: 'w2',
                    typeId: 'cpu'
                },
                {
                    id: 'w3',
                    typeId: 'loadavg'
                }
            ],
            widgetsRight: [
                {
                    id: 'w4',
                    typeId: 'uptime'
                },
                {
                    id: 'w5',
                    typeId: 'memory'
                }
            ]
        }
    }
});
