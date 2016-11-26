import os

from django.apps import apps
from django.utils._os import upath
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
import ramlfications

from ramlgnarok.models import Root, formatter


def get_raml(raml_file):
    raml_file_args = raml_file.split('/')

    for app_config in apps.get_app_configs():
        if not app_config.path:
            continue
        if app_config.name == raml_file_args[0]:
            template_dir = os.path.join(
                app_config.path, 'raml',
            )
            if os.path.isdir(template_dir):
                template_path = upath(template_dir)

                return os.path.join(template_path, raml_file_args[-1])
    raise Exception('raml file not found')


def parse_raml(raml):
    return Root(raml)


def doc_view(request, raml_file):
    return HttpResponse(
        get_template('index.html').render(
            Context({
                'api': parse_raml(ramlfications.load(get_raml(raml_file))),
                'pygments_style': formatter.get_style_defs('.source'),
            })
        )
    )
