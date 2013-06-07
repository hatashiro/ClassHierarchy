# -*- encoding: utf-8 -*-
import threading
import sublime, sublime_plugin
import os
import re
import subprocess

from ClassHierarchyManager import ClassHierarchyManager, set_tab_size, NoSymbolException
from helpers import hierarchy_base_decorator, to_underscore
from HierarchyView import HierarchyView
from settings import setting

set_tab_size(setting('tab_size'))

is_hierarchy_ctags_in_building = False
is_hierarchy_tree_in_loading = False

hierarchy_tree_pool = dict()

class HierarchyTree(object):
    def __init__(self, tree):
        self.tree = tree
        self.view_pool = dict()

def get_hierarchy_tree(project_dir):
    try:
        return hierarchy_tree_pool[project_dir]
    except KeyError:
        return None

def load_hierarchy_tree(project_dir, ctags_file_path):
    hierarchy_tree_pool[project_dir] = HierarchyTree(ClassHierarchyManager())
    hierarchy_tree_pool[project_dir].tree.parse_tags_file(ctags_file_path)

def unload_hierarchy_tree(project_dir):
    hierarchy_tree_pool[project_dir] = None

def check_if_thread_finished(thread, did_finished):
    if thread.is_alive():
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500)
    else:
        did_finished()

def is_busy():
    global is_hierarchy_ctags_in_building, is_hierarchy_tree_in_loading

    if is_hierarchy_ctags_in_building:
        sublime.status_message("Now re/building hierarchy ctags... Please be patient.")
        return True
    if is_hierarchy_tree_in_loading:
        sublime.status_message("Now re/loading hierarchy tree... Please be patient.")
        return True
    return False

class RebuildHierarchyCtagsThread(threading.Thread):
    def __init__(self, ctags_command, ctags_file, project_dir):
        threading.Thread.__init__(self)
        self.ctags_command = ctags_command
        self.ctags_file = ctags_file
        self.project_dir = project_dir

    def run(self):
        global is_hierarchy_ctags_in_building

        ctags_command = self.ctags_command

        # Replace -f arg with the path from setting
        ctags_command = re.sub(" -f *[^ ]+", "", ctags_command)
        ctags_command += " -f %s" % self.ctags_file

        p = subprocess.Popen(ctags_command, cwd=self.project_dir, shell=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()

        is_hierarchy_ctags_in_building = False

class RebuildHierarchyCtags(sublime_plugin.TextCommand):
    def run(self, edit):
        global is_hierarchy_ctags_in_building

        if is_busy():
            return

        is_hierarchy_ctags_in_building = True

        project_dir = self.view.window().folders()[0]
        unload_hierarchy_tree(project_dir)
        sublime.status_message("Re/Building hierarchy ctags... Please be patient.")
        thread = RebuildHierarchyCtagsThread(setting('ctags_command'), setting('ctags_file'), project_dir)

        did_finished = lambda: self.view.run_command('reload_hierarchy_tree')

        thread.start()
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500)

class ReloadHierarchyTreeThread(threading.Thread):
    def __init__(self, project_dir, ctags_file_path):
        threading.Thread.__init__(self)
        self.project_dir = project_dir
        self.ctags_file_path = ctags_file_path

    def run(self):
        global is_hierarchy_tree_in_loading

        load_hierarchy_tree(self.project_dir, self.ctags_file_path)

        is_hierarchy_tree_in_loading = False

class ReloadHierarchyTree(sublime_plugin.TextCommand):
    def run(self, edit, caller=None):
        project_dir = self.view.window().folders()[0]
        ctags_file_path = os.path.join(project_dir, setting('ctags_file'))

        if not os.path.isfile(ctags_file_path):
            sublime.status_message("There's no ctags file for ClassHierarchy. Please check the settings or build the file with 'rebuild_hierarchy_ctags' command.")
            return

        global is_hierarchy_tree_in_loading

        if is_busy():
            return

        is_hierarchy_tree_in_loading = True

        unload_hierarchy_tree(project_dir)
        sublime.status_message("Re/Loading hierarchy tree... Please be patient.")
        thread = ReloadHierarchyTreeThread(project_dir, ctags_file_path)

        if caller:
            did_finished = lambda: self.view.run_command(to_underscore(caller['name']), {'symbol': caller['symbol'], 'window': caller['window']})
        else:
            did_finished = lambda: sublime.status_message("Re/Loading hierarchy tree is finished!")

        thread.start()
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500)

class ShowHierarchyBase(sublime_plugin.TextCommand):
    @hierarchy_base_decorator
    def run(self, edit, view, symbol, window=None):
        self.window = window if window else self.view.window()

        project_dir = view.window().folders()[0]
        hierarchy_tree = get_hierarchy_tree(project_dir)

        if hierarchy_tree:
            if symbol:
                self.show_hierarchy(hierarchy_tree, symbol)
            else:
                self.show_class_panel(hierarchy_tree)
        else:
            view.run_command('reload_hierarchy_tree', {'caller': {'name': self.__class__.__name__, 'symbol': symbol, 'window': self.window}})

    def show_hierarchy(self, hierarchy_tree, symbol):
        try:
            result = self.get_hierarchy(hierarchy_tree, symbol)
            view_name = self.prefix + ': ' + symbol
            hierarchy_view = HierarchyView(view_name, self.window)
            hierarchy_view.set_content(result)

            hierarchy_tree.view_pool[hierarchy_view.name] = hierarchy_view
        except NoSymbolException:
            sublime.status_message("Can't find \"%s\"." % symbol)
            self.show_class_panel(hierarchy_tree)

    def show_class_panel(self, hierarchy_tree):
        class_panel_list = []
        for class_object in hierarchy_tree.tree.class_pool.values():
            if self.class_filter(class_object):
                class_panel_list.append([class_object.name])

        def selected(index):
            symbol = class_panel_list[index][0]
            self.view.run_command(to_underscore(self.__class__.__name__), {'symbol': symbol, 'window': self.window})

        self.window.show_quick_panel(class_panel_list, selected)

class ShowUpwardHierarchy(ShowHierarchyBase):
    prefix = "Upward Hierarchy: "

    def get_hierarchy(self, hierarchy_tree, symbol):
        return hierarchy_tree.tree.get_upward_hierarchy(symbol)

    def class_filter(self, class_object):
        return (len(class_object.parents) > 0)

class ShowDownwardHierarchy(ShowHierarchyBase):
    prefix = "Downward Hierarchy: "

    def get_hierarchy(self, hierarchy_tree, symbol):
        return hierarchy_tree.tree.get_downward_hierarchy(symbol)

    def class_filter(self, class_object):
        return (len(class_object.childs) > 0)

class MouseCommandBase(sublime_plugin.TextCommand):
    def is_in_hierarchy_view(self):
        view_name = self.view.name()
        return (view_name.startswith(ShowUpwardHierarchy.prefix) or view_name.startswith(ShowDownwardHierarchy.prefix))

    def get_row(self):
        return self.view.rowcol(self.view.sel()[0].begin())[0]

class ToggleClassFileLines(MouseCommandBase):
    def run(self, edit):
        if self.is_in_hierarchy_view():
            current_row = self.get_row()

            project_dir = self.view.window().folders()[0]
            hierarchy_tree = get_hierarchy_tree(project_dir)
            hierarchy_tree.view_pool[self.view.name()].toggle_class_file_lines(current_row)

class MoveToFileInHierarchyView(MouseCommandBase):
    def run(self, edit):
        if self.is_in_hierarchy_view():
            current_row = self.get_row()

            project_dir = self.view.window().folders()[0]
            hierarchy_tree = get_hierarchy_tree(project_dir)
            hierarchy_tree.view_pool[self.view.name()].move_to_file(current_row)
