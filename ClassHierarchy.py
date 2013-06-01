# -*- encoding: utf-8 -*-
import threading
import sublime, sublime_plugin

from ClassHierarchyManager import ClassHierarchyManager, set_tab_size, NoSymbolException
from helpers import get_symbol, to_underscore
from settings import setting

class_hierarchy_ctags_command = setting('ctags_command')

class_hierarchy_manager = ClassHierarchyManager()
set_tab_size(setting('tab_size'))

is_hierarchy_tree_in_loading = False
is_hierarchy_tree_loaded = False

def check_if_thread_finished(thread, did_finished):
    if thread.is_alive():
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500);
    else:
        did_finished();

class RebuildHierarchyCtags(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message("Re/Building ctags for hierarchy... Please be patient.")

class ReloadHierarchyTreeThread(threading.Thread):
    def __init__(self, ctags_file_path):
        threading.Thread.__init__(self)
        self.ctags_file_path = ctags_file_path

    def run(self):
        global is_hierarchy_tree_in_loading, is_hierarchy_tree_loaded

        class_hierarchy_manager.parse_tags_file(self.ctags_file_path)
        is_hierarchy_tree_loaded = True
        is_hierarchy_tree_in_loading = False

class ReloadHierarchyTree(sublime_plugin.TextCommand):
    def run(self, edit, caller=None):
        global is_hierarchy_tree_in_loading, is_hierarchy_tree_loaded

        if is_hierarchy_tree_in_loading:
            sublime.status_message("Now re/loading hierarchy tree... Please be patient.")
            return

        is_hierarchy_tree_in_loading = True
        is_hierarchy_tree_loaded = False
        sublime.status_message("Re/Loading hierarchy tree... Please be patient.")
        thread = ReloadHierarchyTreeThread('/Users/junhyunje/Studies/class-hierarchy/tags-hierarchy') # FIXME

        if caller:
            did_finished = lambda: self.view.run_command(to_underscore(caller))
        else:
            did_finished = lambda: sublime.status_message("Re/Loading hierarchy tree is finished!")

        thread.start()
        sublime.set_timeout(lambda: check_if_thread_finished(thread, did_finished), 500);

class ShowUpwardHierarchy(sublime_plugin.TextCommand):
    @get_symbol
    def run(self, edit, view, symbol):
        if symbol:
            try:
                class_hierarchy_manager.show_upward_hierarchy(symbol)
            except NoSymbolException:
                sublime.status_message("Can't find \"%s\"." % symbol)
        else:
            print "Symbol None" # FIXME

class ShowDownwardHierarchy(sublime_plugin.TextCommand):
    @get_symbol
    def run(self, edit, view, symbol):
        if symbol:
            try:
                class_hierarchy_manager.show_downward_hierarchy(symbol)
            except NoSymbolException:
                sublime.status_message("Can't find \"%s\"." % symbol)
        else:
            print "Symbol None" # FIXME
