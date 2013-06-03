# -*- encoding: utf-8 -*-
import threading
import sublime, sublime_plugin
import os
import re
import subprocess

from ClassHierarchyManager import ClassHierarchyManager, set_tab_size, NoSymbolException
from helpers import get_symbol, to_underscore
from HierarchyView import HierarchyView
from settings import setting

set_tab_size(setting('tab_size'))

is_hierarchy_ctags_in_building = False
is_hierarchy_tree_in_loading = False

hierarchy_tree_pool = dict()
def get_hierarchy_tree(project_dir):
    try:
        return hierarchy_tree_pool[project_dir]
    except KeyError:
        return None

def load_hierarchy_tree(project_dir, ctags_file_path):
    hierarchy_tree_pool[project_dir] = ClassHierarchyManager()
    hierarchy_tree_pool[project_dir].parse_tags_file(ctags_file_path)

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
            did_finished = lambda: self.view.run_command(to_underscore(caller))
        else:
            did_finished = lambda: sublime.status_message("Re/Loading hierarchy tree is finished!")

        thread.start()
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500)

class ShowHierarchyBase(sublime_plugin.TextCommand):
    @get_symbol
    def run(self, edit, view, symbol):
        project_dir = view.window().folders()[0]
        hierarchy_tree = get_hierarchy_tree(project_dir)

        if hierarchy_tree:
            if symbol:
                self.show_hierarchy(hierarchy_tree, symbol)
            else:
                print "Symbol None" # FIXME
        else:
            view.run_command('reload_hierarchy_tree', {'caller': self.__class__.__name__})

    def show_hierarchy(self, hierarchy_tree, symbol):
        try:
            result = self.get_hierarchy(hierarchy_tree, symbol)
            view_name = self.view_name + ': ' + symbol
            hierarchy_view = HierarchyView(view_name)
            hierarchy_view.set_content(result)
        except NoSymbolException:
            sublime.status_message("Can't find \"%s\"." % symbol)

class ShowUpwardHierarchy(ShowHierarchyBase):
    def __init__(self, args):
        sublime_plugin.TextCommand.__init__(self, args)
        self.view_name = "Upward Hierarchy"

    def get_hierarchy(self, hierarchy_tree, symbol):
        return hierarchy_tree.get_upward_hierarchy(symbol)

class ShowDownwardHierarchy(ShowHierarchyBase):
    def __init__(self, args):
        sublime_plugin.TextCommand.__init__(self, args)
        self.view_name = "Downward Hierarchy"

    def get_hierarchy(self, hierarchy_tree, symbol):
        return hierarchy_tree.get_downward_hierarchy(symbol)
