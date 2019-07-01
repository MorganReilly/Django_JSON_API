import json

from rest_framework.renderers import JSONRenderer


class ConduitJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'

    def render(self, data, media_type=None, renderer_context=None):
        # If views throws an error 'data' will contain 'errors' key.
        # We want JSONRenderer to handle rendering errors, checking for this
        errors = data.get('errors', None)

        if errors is not None:
            # Let default JSONRenderer handle errors
            return super(ConduitJSONRenderer, self).render(data)

        return json.dumps({
            self.object_label: data
        })
