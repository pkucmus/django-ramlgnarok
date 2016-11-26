from django import template
from django.utils.safestring import mark_safe
import markdown


register = template.Library()


@register.filter('md')
def parse_markdown(markdown_content):
    if not markdown_content:
        return markdown_content
    return mark_safe(markdown.markdown(
        markdown_content, [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'pygments_style': 'monokai'
            }
        }
    ))
