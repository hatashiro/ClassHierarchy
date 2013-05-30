# -*- encoding: utf-8 -*-
import sublime

def get_settings():
    return sublime.load_settings("CTagsHierarchy.sublime-settings")

def get_setting(key, default=None, view=None):
    try:
        if view == None:
            view = sublime.active_window().active_view()
        s = view.settings()
        if s.has("ctagshierarchy_%s" % key):
            return s.get("ctagshierarchy_%s" % key)
    except:
        pass
    return get_settings().get(key, default)

setting = get_setting
