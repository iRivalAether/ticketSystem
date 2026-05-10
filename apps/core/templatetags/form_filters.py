from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_classes):
    existing_classes = field.field.widget.attrs.get("class", "")
    combined_classes = f"{existing_classes} {css_classes}".strip()
    return field.as_widget(attrs={"class": combined_classes})
