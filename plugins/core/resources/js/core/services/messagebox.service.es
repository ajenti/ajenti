angular.module('core').service('messagebox', function($timeout, $q) {
    this.messages = [];

    this.show = (options) => {
        let q = $q.defer();
        options.visible = true;
        options.q = q;
        this.messages.push(options);
        return {
            messagebox: options,
            then: (f) => q.promise.then(f),
            catch: (f) => q.promise.catch(f),
            finally: (f) => q.promise.finally(f),
            close: () => this.close(options)
        };
    };

    this.prompt = (prompt, value) => {
        value = value || ''
        return this.show({
            prompt,
            value,
            positive: 'OK',
            negative: 'Cancel'
        });
    };

    this.close = (msg) => {
        msg.visible = false;
        return $timeout(() => {
            this.messages.remove(msg);
        }, 1000);
    };

    return this;
});
