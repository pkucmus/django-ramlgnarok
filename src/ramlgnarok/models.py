from __future__ import unicode_literals

from collections import OrderedDict

from django.utils.safestring import mark_safe
from rest_framework.renderers import JSONRenderer
from rest_framework_yaml.renderers import YAMLRenderer
from rest_framework_xml.renderers import XMLRenderer

from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype
from pygments.formatters import HtmlFormatter


METHODS = ('get', 'patch', 'put', 'post', 'delete', 'options', 'head', )

formatter = HtmlFormatter(style='trac', linenos=False, cssclass='source')


class Root(object):

    def __init__(self, data):
        self.title = data['title']
        self.version = data['version']
        self.base_uri = data['baseUri']
        self.media_types = data.get('mediaType', None)

        self.security_schemes = OrderedDict(
            [
                (key, SecurityScheme(key, self, sec_data))
                for key, sec_data
                in data.get('securitySchemes', {}).iteritems()
            ]
        )
        self.secured_by = [
            self.security_schemes.get(sec_scheme)
            for sec_scheme in data.get('securedBy', [])
        ]

        self.toc = OrderedDict()

        self.endpoints = []
        for key, data in data.iteritems():
            if key.startswith('/'):
                if data is None:
                    continue
                self.add_child(Resource(self, self, key, data))

    def add_toc(self, name, node):
        self.toc[name] = node

    def add_child(self, child):
        self.endpoints.append(child)
        self.add_toc(child.name, child)


class SecurityScheme(object):

    def __init__(self, name, root, data):
        self.type = data['type']
        self.name = data.get('displayName', name)
        self.description = data.get('description')

        described_by = data.get('describedBy', {})

        self.headers = OrderedDict(
            [
                (key, Header(key, header_data))
                for key, header_data
                in described_by.get('headers', {}).iteritems()
            ]
        )
        self.responses = OrderedDict(
            [
                (key, Response(key, root, resp_data))
                for key, resp_data
                in described_by.get('responses', {}).iteritems()
            ]
        )
        self.query_parameters = OrderedDict()


class Header(object):

    def __init__(self, name, data):
        self.name = name
        self.description = data.get('description')
        self.required = data.get('required')

        self.type = data.get('type', 'string')
        if self.type[-1] == '?':
            self.required = False
            self.type = self.type[:-1]
        self.example = data.get('example')


class Resource(object):

    def __init__(self, parent, root, path, data):
        self.name = data.get('displayName')
        self.path = path
        self.id = path.replace('/', '-').strip('-')
        self.description = data.get('description')
        self.secured_by = self.get_secured_by(
            root, parent, data.get('securedBy')
        )

        self.methods = OrderedDict()
        self.childs = []
        for key, data in data.iteritems():
            if key.startswith('/'):
                if data is None:
                    continue
                abs_path = ''.join([path, key])
                parent.add_child(Resource(self, root, abs_path, data))
                if parent is not root:
                    root.add_child(Resource(self, root, abs_path, data))
            elif key.lower() in METHODS:
                self.methods[key] = Method(key, root, self, data)

        self.traits = []
        self.uri_parameters = None

    def add_child(self, child):
        self.childs.append(child)

    def get_secured_by(self, root, parent, secured_by):
        if secured_by is None:
            return parent.secured_by
        security_schemes = secured_by

        return [
            root.security_schemes.get(sec_scheme)
            for sec_scheme in security_schemes
        ]


class Method(object):

    def __init__(self, name, root, resource, data):
        self.id = '{}-{}'.format(resource.id, name).strip('-')
        self.name = name
        self.description = data.get('description')
        self.secured_by = self.get_secured_by(
            root, resource, data.get('securedBy')
        )

        self.body = []
        if data.get('body') is not None:
            self.body = list(Body.build_bodies(root, data['body']))

        self.responses = OrderedDict()
        self.headers = OrderedDict()
        for sec_scheme in self.secured_by:
            self.headers.update(sec_scheme.headers)
            self.responses.update(sec_scheme.responses)

        self.responses.update(OrderedDict(
            [
                (status_code, Response(status_code, root, data))
                for status_code, resp_data
                in data.get('responses', {}).iteritems()
            ]
        ))
        self.responses = OrderedDict(sorted(self.responses.iteritems()))
        self.headers.update(OrderedDict(
            [
                (key, Header(key, header_data))
                for key, header_data in data.get('headers', {})
            ]
        ))
        self.query_parameters = []
        self.queryString = []
        self.protocols = []
        self.traits = []

    def get_secured_by(self, root, parent, secured_by):
        if secured_by is None:
            return parent.secured_by
        security_schemes = secured_by

        return [
            root.security_schemes.get(sec_scheme)
            for sec_scheme in security_schemes
        ]


class Response(object):

    def __init__(self, status_code, root, data):
        self.status_code = status_code
        self.description = status_code
        if data.get('body') is not None:
            self.body = list(Body.build_bodies(root, data['body']))
        self.headers = [
            Header(name, header_data)
            for name, header_data in data.get('headers', {}).iteritems()
        ]


class Body(object):

    renderers = {
        'application/json': JSONRenderer,
        'application/yaml': YAMLRenderer,
        'application/xml': XMLRenderer,
    }

    def __init__(self, root, data, media_type):
        self.media_type = media_type
        self.examples = data.get('examples', {})
        self.rendered = {}
        for name, example in self.examples.iteritems():
            self.rendered[name] = self.render_example(example)
        self.type = data.get('type', 'object')

    def render_example(self, example):
        renderer = self.renderers[self.media_type]
        rendered = renderer().render(example, renderer_context={'indent': 4})
        lexer = get_lexer_for_mimetype(self.media_type)
        return mark_safe(highlight(rendered, lexer, formatter))

    @classmethod
    def build_bodies(cls, root, data):
        media_types_defined = False
        for key, value in data.iteritems():
            if len(key.split('/')) == 2:
                media_types_defined = True
                yield cls(root, value, key)
            else:
                break
        if not media_types_defined:
            for media_type in root.media_types:
                yield cls(root, data, media_type)
