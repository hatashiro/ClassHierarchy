# -*- encoding: utf-8 -*-
import sublime, sublime_plugin

from ClassHierarchyManager import ClassHierarchyManager, set_tab_size, NoSymbolException
from helpers import get_symbol
from settings import setting

class_hierarchy_ctags_command = setting('ctags_command')

class_hierarchy_manager = ClassHierarchyManager()
set_tab_size(setting('tab_size'))

class RebuildHierarchy(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message("Re/Building hierarchy... Please be patient.")
        class_hierarchy_manager.parse_tags_file('/Users/junhyunje/Studies/class-hierarchy/tags-hierarchy') # FIXME

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
