angular.module('core').filter('bytes', gettext =>
    (bytes, precision) => {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) {
            return '-';
        }
        if (bytes === 0) {
            return gettext('0 bytes');
        }
        if (typeof precision === 'undefined') {
            precision = 1;
        }
        let units = [
            gettext('bytes'),
            gettext('KB'),
            gettext('MB'),
            gettext('GB'),
            gettext('TB'),
            gettext('PB'),
        ];
        let number = Math.floor(Math.log(bytes) / Math.log(1024));

        let x = (bytes / Math.pow(1024, Math.floor(number)));
        if (number === 0) {
            x = Math.floor(x);
        } else {
            x = x.toFixed(precision);
        }

        return x +  ' ' + units[number];
    }
);

angular.module('core').filter('ordinal', gettext =>
    (input) => {
        if (isNaN(input) || input === null) {
            return input;
        }

        let s = [
            gettext('th'),
            gettext('st'),
            gettext('nd'),
            gettext('rd'),
        ];
        let v = input % 100;
        return input + (s[(v - 20) % 10] || s[v] || s[0]);
    }
);

angular.module('core').filter('page', () =>
    (list, page, pageSize) => {
        if (list && pageSize) {
            return list.slice((page - 1) * pageSize, page * pageSize);
        }
    }
);

angular.module('core').filter('rankMatch', () =>
    (input, field, query) => {
        if (!input) {
            return input;
        }
        let rgx = new RegExp(query, 'gi');
        for (let i = 0; i < input.length; i++) {
            let item = input[i];
            let points = 0;
            let data = item[field];
            points += (data.match(rgx) || []).length;
            if (data === query) {
                points += 50;
            }
            if (data.indexOf(query) === 0) {
                points += 10;
            }
            item.rank = points;
        }
        return input;
    }
);


angular.module('core').filter('time', () =>
    (time, frac) => {
        if (time === null || !angular.isDefined(time)) {
            return '--:--:--';
        }
        let s = '';
        if (time >= 3600 * 24) {
            s += Math.floor(time / 3600 / 24) + 'd ';
        }
        s += (`${Math.floor(time / 60 / 60) % 24}`).lpad('0', 2) + ':';
        s += (`${Math.floor(time / 60) % 60}`).lpad('0', 2) + ':';
        s += (`${Math.floor(time) % 60}`).lpad('0', 2);
        if (frac) {
            s += `.${(`${Math.floor((time - Math.floor(time)) * Math.pow(10, frac))}`).lpad('0', frac + 0)}`;
        }
        return s;
    }
);
