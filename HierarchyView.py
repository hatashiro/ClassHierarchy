# -*- encoding: utf-8 -*-
import sublime

class HierarchyView(object):
    def __init__(self, name):
        self.name = name
        self.file_lines = dict()
        self.set_view()

    def set_content(self, content):
        self.view.set_read_only(False)

        edit = self.view.begin_edit()
        self.view.insert(edit, 0, content)
        self.view.end_edit(edit)

        self.fold_files(content)

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
        self.view.set_syntax_file('Packages/ClassHierarchy/syntax/ClassHierarchy.tmLanguage')

    def fold_files(self, content):
        """
        file_lines: dict()
            key: the line number of the line that contains the class name
            value: the list that contains file line numbers
        """
        current_class = None
        for line_number, line in enumerate(content.split("\n")):
            line = line.strip()
            if not line.startswith("|"):
                self.file_lines[line_number] = []
                current_class = self.file_lines[line_number]
            else:
                current_class.append(line_number)

        for class_line in self.file_lines.keys():
            self.toggle_class_file_lines(class_line)

    def get_file_region(self, row):
        file_lines = None
        try:
            file_lines = self.file_lines[row]
        except KeyError:
            for lines in self.file_lines.values():
                if row in lines:
                    file_lines = lines
                    break

        region_from = self.view.text_point(min(file_lines), 0) - 1
        region_to = self.view.text_point(max(file_lines) + 1, 0) - 1

        # Fix for the last line
        if region_to + 1 == self.view.size():
            region_to += 1

        return sublime.Region(region_from, region_to)

    def toggle_class_file_lines(self, row):
        if not self.view.fold(self.get_file_region(row)):
            self.view.unfold(self.get_file_region(row))
