from django.conf.urls import url

from ramlgnarok.views import doc_view

urlpatterns = [
    url(r'^(?P<raml_file>.+)$', doc_view, name='doc_view'),
]
