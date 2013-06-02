# -*- encoding: utf-8 -*-
import sublime

class HierarchyView(object):
    def __init__(self, name):
        self.name = name
        self.set_view()

    def set_content(self, content):
        self.view.set_read_only(False)

        edit = self.view.begin_edit()
        self.view.insert(edit, 0, content)
        self.view.end_edit(edit)

        self.view.set_scratch(True)
        self.view.set_read_only(True)

    def empty_view(self):
        self.view.set_read_only(False)

        e = self.view.begin_edit()
        self.view.erase(e, sublime.Region(0, self.view.size()))

        self.view.end_edit(e)

        self.view.set_read_only(True)

    def set_view(self):
        window = sublime.active_window()
        for view in window.views():
            if view.name() == self.name:
                self.view = view
                self.empty_view()
                window.focus_view(self.view)
                return
        self.view = sublime.active_window().new_file()
        self.view.set_name(self.name)
