import re

class ApacheConfig(object):

    re_comment = re.compile(r"""^#.*$""")
    re_section_start = re.compile(r"""^<(?P<name>[^/\s>]+)\s*(?P<value>[^>]+)?>$""")
    re_section_end = re.compile(r"""^</(?P<name>[^\s>]+)\s*>$""")
    #re_statement = re.compile(r"""^(?P<name>[^\s]+)\s*(?P<value>.+)?$""")

    def __init__(self, name, values=[], section=False):
        self.name = name
        self.children = []
        self.values = values
        self.section = section


    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return child


    def find(self, path):
        """Return the first element wich matches the path.
        """
        pathelements = path.strip("/").split("/")
        if pathelements[0] == '':
            return self
        return self._find(pathelements)


    def _find(self, pathelements):
        if pathelements: # there is still more to do ...
            next = pathelements.pop(0)
            for child in self.children:
                if child.name == next:
                    result = child._find(pathelements)
                    if result:
                        return result
            return None
        else: # no pathelements left, result is self
            return self


    def findall(self, path):
        """Return all elements wich match the path.
        """
        pathelements = path.strip("/").split("/")
        if pathelements[0] == '':
            return [self]
        return self._findall(pathelements)


    def _findall(self, pathelements):
        if pathelements: # there is still more to do ...
            result = []
            next = pathelements.pop(0)
            for child in self.children:
                if child.name == next:
                    result.extend(child._findall(pathelements))
            return result
        else: # no pathelements left, result is self
            return [self]
            

    def print_r(self, indent = -1):
        """Recursively print node.
        """
        if self.section:
            if indent >= 0:
                print "    " * indent + "<" + self.name + " " + " ".join(self.values) + ">"
            for child in self.children:
                child.print_r(indent + 1)
            if indent >= 0:
                print "    " * indent + "</" + self.name + ">"
        else:
            if indent >= 0:
                print "    " * indent + self.name + " " + " ".join(self.values)


    @classmethod
    def parse_file(cls, file):
        """Parse a file.
        """
        f = open(file)
        root = cls._parse(f)
        f.close()
        return root


    @classmethod
    def parse_string(cls, string):
        """Parse a string.
        """
        return cls._parse(string.splitlines())


    @classmethod
    def _parse(cls, itobj):
        root = node = ApacheConfig('', section=True)
        for line in itobj:
            line = line.strip()
            if (len(line) == 0) or cls.re_comment.match(line):
                continue

            match = cls.re_section_start.match(line)
            if match:
                values = match.group("value").split()
                new_node = ApacheConfig(match.group("name"), values=values, section=True)
                node = node.add_child(new_node)
                continue
            match = cls.re_section_end.match(line)
            if match:
                if node.name != match.group("name"):
                    raise Exception("Section mismatch: '"+match.group("name")+"' should be '"+node.name+"'")
                node = node.parent
                continue
            values = line.split()
            name = values.pop(0)
            node.add_child(ApacheConfig(name, values=values, section=False))
        return root