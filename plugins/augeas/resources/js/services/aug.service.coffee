angular.module('ajenti.augeas').service 'AugeasConfig', () ->
    class AugeasNode
        constructor: () ->
            @children = []

        fullPath: () ->
            if @path
                return @path

            total = 0
            index = null
            for child in @parent.children
                if child.name == @name
                    total += 1
                if child == this
                    index = total
            if total > 1
                return "#{@parent.fullPath()}/#{@name}[#{index}]"
            else
                return "#{@parent.fullPath()}/#{@name}"

    class AugeasConfig
        constructor: (data) ->
            @root = @__construct(data)
            @root.path = data.path

        serialize: (node) ->
            node ?= @root
            data = {}
            data.path = node.fullPath()
            data.name = node.name
            data.value = node.value
            data.children = (@serialize(c) for c in node.children)
            return data

        __construct: (data, parent) ->
            node = new AugeasNode()
            node.name = data.name
            node.value = data.value
            node.parent = parent
            for c in data.children
                node.children.push @__construct(c, node)
            return node

        relativize: (path) ->
            return path.substring(@root.path.length + 1)

        getNode: (path) ->
            matches = @matchNodes(path)
            if matches.length == 0
                return null
            return matches[0]

        get: (path) ->
            node = @getNode(path)
            if not node
                return null
            return node.value

        set: (path, value, node) ->
            if not node
                node = @root
                if path[0] == '/'
                    path = @relativize(path)

            if not path
                node.value = value
                return

            if path.indexOf('/') == -1
                q = path
                remainder = null
            else
                q = path.substring(0, path.indexOf('/'))
                remainder = path.substring(path.indexOf('/') + 1)

            child = @matchNodes(q, node)[0]
            if not child
                child = new AugeasNode()
                child.parent = node
                child.name = q
                node.children.push child

            @set(remainder, value, child)

        setd: (path, value) ->
            if not value
                @remove(path)
            else
                @set(path, value)

        model: (path, setd) ->
            setfx = (p, v) => if setd then @setd(p, v) else @set(p, v)
            fx = (value) =>
                if angular.isDefined(value)
                    setfx(path, value)
                return @get(path)

            return fx

        insert: (path, value, index) ->
            matches = @matchNodes(path)
            if matches.length == 0
                @set(path, value)
                return path
            else
                node = matches[0].parent
                index ?= node.children.indexOf(matches[matches.length - 1]) + 1
                child = new AugeasNode()
                child.parent = node
                child.name = path.substring(path.lastIndexOf('/') + 1)
                child.value = value
                node.children.splice index, 0, child
                return child.fullPath()

        remove: (path) ->
            for node in @matchNodes(path)
                node.parent.children.remove(node)

        match: (path, node) -> (x.fullPath() for x in @matchNodes(path, node))

        matchNodes: (path, node) ->
            if not node
                node = @root
                if path[0] == '/'
                    path = @relativize(path)

            if path.indexOf('/') == -1
                q = path
                remainder = null
            else
                q = path.substring(0, path.indexOf('/'))
                remainder = path.substring(path.indexOf('/') + 1)

            if q.indexOf('[') == -1
                index = null
            else
                index = parseInt(q.substring(q.indexOf('[') + 1, q.indexOf(']'))) - 1
                q = q.substring(0, q.indexOf('['))

            matches = []
            rx = new RegExp('^' + q + '$')
            for child in node.children
                if rx.test(child.name)
                    matches.push child

            if index != null
                if matches.length <= index
                    matches = []
                else
                    matches = [matches[index]]

            if not remainder
                return matches

            deepMatches = []
            for match in matches
                for sm in @matchNodes(remainder, match)
                    deepMatches.push sm

            return deepMatches

    @get = (data) ->
        return new AugeasConfig(data)
    
    return this
