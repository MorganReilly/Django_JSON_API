from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'ProfileDoesNotExist': _handle_generic_error,
        'ValidationError': _handle_generic_error
    }
    excepption_class = exc.__class__.__name__

    if excepption_class in handlers:
        return handlers[excepption_class](exc, context, response)
    return response


def _handle_generic_error(exc, content, response):
    response.data = {
        'errors': response.data
    }
    return response
