# -*- encoding: utf-8 -*-
import sublime

def get_setting(settings, key):
    if settings.has(key):
        return settings.get(key)
    else:
        return None

def get_setting_from_view(key):
    try:
        view = sublime.active_window().active_view()
        return get_setting(view.settings(), "class_hierarchy_%s" % key)
    except:
        return None

def get_setting_from_preferences(key):
    settings = sublime.load_settings("Preferences.sublime-settings")
    return get_setting(settings, "class_hierarchy_%s" % key)

def get_setting_from_plugin(key):
    settings = sublime.load_settings("ClassHierarchy.sublime-settings")
    return get_setting(settings, key)

def setting(key, default=None, view=None):
    value = get_setting_from_view(key)
    if value:
        return value

    value = get_setting_from_preferences(key)
    if value:
        return value

    value = get_setting_from_plugin(key)
    if value:
        return value
