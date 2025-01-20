from django.utils.deprecation import MiddlewareMixin


class SecurityMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class ReferrerPolicyMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response


class CSPMiddleware(MiddlewareMixin):
  def process_response(self, request, response):
    # response['Content-Security-Policy-Report-Only'] = "policy"
    response['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response