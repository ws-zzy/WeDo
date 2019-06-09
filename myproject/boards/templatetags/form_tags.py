from django import template
register = template.Library()

@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__

@register.filter
def input_class(bound_field):
    css_class = ''

    if bound_field.form.is_bound:
        if (not bound_field.errors) and (field_type(bound_field) != 'PasswordInput'):
            css_class = 'is-valid'
        elif bound_field.errors:
            css_class = 'is-invalid'
    return 'form-control {}'.format(css_class)