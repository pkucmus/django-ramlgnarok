
# {{ api.title }}

### {{ api.version }}
### {{ api.baseUri }}

# Authentication

{{ api.securitySchemes }}

{% for endpoint in api.endpoints %}

# {{ endpoint.name }}
{{ endpoint.secured_by }}

{% for method in endpoint.methods.values %}
## {{ method.name }}

{% if method.responses %}
Responses:
{% for response in method.responses %}
### {{ response.status_code }}
{% endfor %}
{% endif %}

{% endfor %}


{{ endpoint }}

{% endfor %}
