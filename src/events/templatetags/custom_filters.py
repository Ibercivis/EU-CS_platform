from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': field.field.widget.attrs.get('class', '') + ' ' + css_class})
