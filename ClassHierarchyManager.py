# -*- encoding: utf-8 -*-

tab_size = 4
def set_tab_size(ts):
    global tab_size
    tab_size = ts

class NoSymbolException(Exception):
    pass

class Class(object):
    def __init__(self, name):
        self.name = name
        self.filepaths = set()
        self.parents = set()
        self.childs = set()

    def inherits(self, parent):
        self.parents.add(parent)
        parent.childs.add(self)

    def add_filepath(self, path):
        self.filepaths.add(path)

    def get_info(self, indent=''):
        result = indent + self.name
        for filepath in self.filepaths:
            result += "\n" + indent + '|' + filepath
        return result

    def get_upward_hierarchy(self, indent=''):
        result = self.get_info(indent)

        for parent in sorted(self.parents, key=lambda cls: cls.name):
            result += "\n" + parent.get_upward_hierarchy(indent + ' ' * tab_size)

        return result

    def get_downward_hierarchy(self, indent=''):
        result = self.get_info(indent)

        for child in sorted(self.childs, key=lambda cls: cls.name):
            result += "\n" + child.get_downward_hierarchy(indent + ' ' * tab_size)

        return result

class ClassHierarchyManager(object):
    def __init__(self):
        self.class_pool = dict()

    def get_class(self, class_name):
        try:
            cls = self.class_pool[class_name]
        except KeyError:
            cls = Class(class_name)
            self.class_pool[class_name] = cls
        return cls

    def parse_tags_file(self, tags_filename):
        tagsfile = open(tags_filename)
        while True:
            lines = tagsfile.readlines(100)
            if not lines:
                break
            for line in lines:
                tokens = line.strip().split("\t")

                class_name = tokens[0]
                filepath = tokens[1]

                cls = self.get_class(class_name)
                cls.add_filepath(filepath)

                inherits = tokens[len(tokens) - 1]
                if inherits.startswith('inherits:'):
                    parents = inherits[9:].split(',')
                    for parent in parents:
                        if "::" in parent:
                            parent_with_namespace = parent
                            parent = parent_with_namespace.split("::")[-1]
                            if class_name == parent:
                                parent = parent_with_namespace
                        if class_name != parent:
                            cls.inherits(self.get_class(parent))

    def get_upward_hierarchy(self, symbol):
        try:
            cls = self.class_pool[symbol]
        except KeyError:
            raise NoSymbolException
        return cls.get_upward_hierarchy()

    def get_downward_hierarchy(self, symbol):
        try:
            cls = self.class_pool[symbol]
        except KeyError:
            raise NoSymbolException
        return cls.get_downward_hierarchy()
