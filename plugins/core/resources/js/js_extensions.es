Array.prototype.remove = function(...args) {
    let output = [];
    for (let i = 0; i < args.length; i++) {
        let arg = args[i];
        let index = this.indexOf(arg);
        if (index !== -1) { output.push(this.splice(index, 1)); }
    }
    if (args.length === 1) { output = output[0]; }
    return output;
};


Array.prototype.contains = function(v) {
    return this.indexOf(v) > -1;
};


Array.prototype.toggleItem = function(v) {
    if (this.contains(v)) {
        this.remove(v);
    } else {
        this.push(v);
    }
};


String.prototype.lpad = function(padString, length) {
    let str = this;
    while (str.length < length) {
        str = padString + str;
    }
    return str;
};
