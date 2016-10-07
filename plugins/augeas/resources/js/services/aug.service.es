angular.module('ajenti.augeas').service('AugeasConfig', function() {
    class AugeasNode {
        constructor() {
            this.children = [];
        }

        fullPath() {
            if (this.path) {
                return this.path;
            }

            let total = 0;
            let index = null;
            for (let i = 0; i < this.parent.children.length; i++) {
                let child = this.parent.children[i];
                if (child.name === this.name) {
                    total += 1;
                }
                if (child === this) {
                    index = total;
                }
            }
            if (total > 1) {
                return `${this.parent.fullPath()}/${this.name}[${index}]`;
            } else {
                return `${this.parent.fullPath()}/${this.name}`;
            }
        }
    }

    class AugeasConfig {
        constructor(data) {
            this.root = this.__construct(data);
            this.root.path = data.path;
        }

        serialize(node) {
            if (typeof node === 'undefined' || node === null) { node = this.root; }
            let data = {};
            data.path = node.fullPath();
            data.name = node.name;
            data.value = node.value;
            data.children = (node.children.map((c) => this.serialize(c)));
            return data;
        }

        __construct(data, parent) {
            let node = new AugeasNode();
            node.name = data.name;
            node.value = data.value;
            node.parent = parent;
            for (let i = 0; i < data.children.length; i++) {
                let c = data.children[i];
                node.children.push(this.__construct(c, node));
            }
            return node;
        }

        relativize(path) {
            return path.substring(this.root.path.length + 1);
        }

        getNode(path) {
            let matches = this.matchNodes(path);
            if (matches.length === 0) {
                return null;
            }
            return matches[0];
        }

        get(path) {
            let node = this.getNode(path);
            if (!node) {
                return null;
            }
            return node.value;
        }

        set(path, value, node) {
            if (!node) {
                node = this.root;
                if (path[0] === '/') {
                    path = this.relativize(path);
                }
            }

            if (!path) {
                node.value = value;
                return;
            }

            if (path.indexOf('/') === -1) {
                var q = path;
                var remainder = null;
            } else {
                var q = path.substring(0, path.indexOf('/'));
                var remainder = path.substring(path.indexOf('/') + 1);
            }

            let child = this.matchNodes(q, node)[0];
            if (!child) {
                child = new AugeasNode();
                child.parent = node;
                child.name = q;
                node.children.push(child);
            }

            return this.set(remainder, value, child);
        }

        setd(path, value) {
            if (!value) {
                return this.remove(path);
            } else {
                return this.set(path, value);
            }
        }

        model(path, setd) {
            let setfx = (p, v) => setd ? this.setd(p, v) : this.set(p, v);
            let fx = value => {
                if (angular.isDefined(value)) {
                    setfx(path, value);
                }
                return this.get(path);
            };

            return fx;
        }

        insert(path, value, index) {
            let matches = this.matchNodes(path);
            if (matches.length === 0) {
                this.set(path, value);
                return path;
            } else {
                let node = matches[0].parent;
                if (typeof index === 'undefined' || index === null) { index = node.children.indexOf(matches[matches.length - 1]) + 1; }
                let child = new AugeasNode();
                child.parent = node;
                child.name = path.substring(path.lastIndexOf('/') + 1);
                child.value = value;
                node.children.splice(index, 0, child);
                return child.fullPath();
            }
        }

        remove(path) {
            return this.matchNodes(path).map((node) =>
                node.parent.children.remove(node));
        }

        match(path, node) { return (this.matchNodes(path, node).map((x) => x.fullPath())); }

        matchNodes(path, node) {
            if (!node) {
                node = this.root;
                if (path[0] === '/') {
                    path = this.relativize(path);
                }
            }

            if (path.indexOf('/') === -1) {
                var q = path;
                var remainder = null;
            } else {
                var q = path.substring(0, path.indexOf('/'));
                var remainder = path.substring(path.indexOf('/') + 1);
            }

            if (q.indexOf('[') === -1) {
                var index = null;
            } else {
                var index = parseInt(q.substring(q.indexOf('[') + 1, q.indexOf(']'))) - 1;
                var q = q.substring(0, q.indexOf('['));
            }

            let matches = [];
            let rx = new RegExp(`^${q}$`);
            for (let i = 0; i < node.children.length; i++) {
                let child = node.children[i];
                if (rx.test(child.name)) {
                    matches.push(child);
                }
            }

            if (index !== null) {
                if (matches.length <= index) {
                    matches = [];
                } else {
                    matches = [matches[index]];
                }
            }

            if (!remainder) {
                return matches;
            }

            let deepMatches = [];
            for (let j = 0; j < matches.length; j++) {
                let match = matches[j];
                let iterable = this.matchNodes(remainder, match);
                for (let k = 0; k < iterable.length; k++) {
                    let sm = iterable[k];
                    deepMatches.push(sm);
                }
            }

            return deepMatches;
        }
    }

    this.get = data => new AugeasConfig(data);

    return this;
});
