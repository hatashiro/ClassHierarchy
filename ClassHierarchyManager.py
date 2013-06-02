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

    def show_info(self, indent=''):
        print indent + self.name
        for filepath in self.filepaths:
            print indent + '|' + filepath

    def show_upward_hierarchy(self, indent=''):
        self.show_info(indent)

        if len(self.parents) == 0:
            return
        for parent in sorted(self.parents, key=lambda cls: cls.name):
            parent.show_upward_hierarchy(indent + ' ' * tab_size)

    def show_downward_hierarchy(self, indent=''):
        self.show_info(indent)

        if len(self.childs) == 0:
            return
        for child in sorted(self.childs, key=lambda cls: cls.name):
            child.show_downward_hierarchy(indent + ' ' * tab_size)

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
                        cls.inherits(self.get_class(parent))

    def show_upward_hierarchy(self, symbol):
        try:
            cls = self.class_pool[symbol]
        except KeyError:
            raise NoSymbolException
        cls.show_upward_hierarchy()

    def show_downward_hierarchy(self, symbol):
        try:
            cls = self.class_pool[symbol]
        except KeyError:
            raise NoSymbolException
        cls.show_downward_hierarchy()
