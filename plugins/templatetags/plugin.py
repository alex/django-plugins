from django import template

from plugins.models import Plugin

register = template.Library()

"""
Usage:
{% apply_plugin some_obj %}
or
{% apply_plugin some_obj as new_obj %}
"""

class ApplyPluginNode(template.Node):
    def __init__(self, object_name, varname=None):
        self.object_name, self.varname = object_name, varname
    
    def render(self, context):
        obj = context[self.object_name]
        plgs = Plugin.objects.filter(active=True, acts_on=obj.__class__.__name__)
        for plg in plgs:
            plg_cls = plg.get_class()
            inst = plg_cls(obj)
            obj = inst.execute()
        if self.varname:
            context[self.varname] = obj
        else:
            context[self.object_name] = obj
        return ''
        

def apply_plugin(parser, token):
    bits = token.contents.split()
    if len(bits) == 4:
        if bits[2] != 'as':
            raise template.TemplateSyntaxError, "apply_plugin tag's second argument must be 'as'"
        return ApplyPluginNode(bits[1], bits[3])
    elif len(bits) == 2:
        return ApplyPluginNode(bits[1])
    else:
        raise template.TemplateSyntaxError, "apply_plugin tag takes either 1 or 3 arguments"
register.tag(apply_plugin.__name__, apply_plugin)
