import json

from rest_framework.renderers import JSONRenderer


class BaseJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)
        if errors:
            return super(BaseJSONRenderer).render(data)
        return json.dumps({
            'data': data
        })

