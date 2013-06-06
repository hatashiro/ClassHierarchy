# -*- encoding: utf-8 -*-
import os
import sublime

class HierarchyView(object):
    def __init__(self, name, window=None):
        self.name = name
        self.window = window if window else sublime.active_window()

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
        for view in self.window.views():
            if view.name() == self.name:
                self.view = view
                self.empty_view()
                self.window.focus_view(self.view)
                return
        self.view = self.window.new_file()
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
        if not self.view.unfold(self.get_file_region(row)):
            if row in self.file_lines.keys():
                self.view.fold(self.get_file_region(row))

    def move_to_file(self, row):
        file_path = self.get_file_path_in_row(row)
        if file_path:
            window = sublime.active_window()
            class_view = window.open_file(os.path.join(window.folders()[0], file_path))

            self.highlight_class_name(class_view, self.get_class_name_for_row(row))

    def get_class_name_for_row(self, row):
        for class_line, file_lines in self.file_lines.iteritems():
            if row == class_line or row in file_lines:
                return self.get_text_in_row(class_line).strip()
        return None

    def get_file_path_in_row(self, row):
        for lines in self.file_lines.values():
            if row in lines:
                return self.get_text_in_row(row).strip()[1:]
        return ""

    def get_text_in_row(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def highlight_class_name(self, view, class_name):
        def load_finished():
            class_regex = ".*class\s+(%s)[^a-zA-z0-9_]\s*[:]?([^{]+)\{" % class_name # FIXME: C++ only
            class_region = view.find(class_regex, 0)

            if class_region:
                # Focus and highlight the class
                view.show(class_region)
                view.add_regions("class_hierarchy_class_found", [class_region], 'source', 'dot', sublime.DRAW_OUTLINED)

                # Unhighlight after 5 seconds.
                sublime.set_timeout(lambda: view.erase_regions("class_hierarchy_class_found"), 5000)

        def check_if_loaded():
            if view.is_loading():
                sublime.set_timeout(lambda: check_if_loaded(), 100)
            else:
                load_finished();

        # Wait until the view is loaded
        sublime.set_timeout(lambda: check_if_loaded(), 100)
