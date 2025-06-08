import logging
from datetime import datetime, time, timedelta
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import threading
import re

# Configure a logger for requests
request_logger = logging.getLogger('request_logger')
request_logger.setLevel(logging.INFO)
# Ensure the log file handler is added only once
if not request_logger.handlers:
    file_handler = logging.FileHandler(settings.BASE_DIR / 'requests.log')
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    request_logger.addHandler(file_handler)


# Thread-safe dictionary to store IP request counts and timestamps
# Using a lock for thread safety as __call__ can be accessed concurrently
ip_request_data = {}
ip_request_data_lock = threading.Lock()

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log each user's request to a file.
    Logs timestamp, user, and request path.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Ensure the logger is configured only once when the middleware is initialized

    def __call__(self, request):
        # Log request information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        request_logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access to the messaging app during certain hours.
    Denies access between 9 PM (21:00) and 6 AM (06:00).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_start_hour = 21 # 9 PM
        self.restricted_end_hour = 6   # 6 AM

    def __call__(self, request):
        current_time = datetime.now().time()

        # Define the restricted time range
        # If start hour > end hour, it means the range spans across midnight
        if self.restricted_start_hour > self.restricted_end_hour:
            # e.g., 9 PM to 6 AM (next day)
            is_restricted = (current_time >= time(self.restricted_start_hour, 0)) or \
                            (current_time < time(self.restricted_end_hour, 0))
        else:
            # e.g., 9 AM to 6 PM (same day) - not the case here, but for completeness
            is_restricted = (current_time >= time(self.restricted_start_hour, 0)) and \
                            (current_time < time(self.restricted_end_hour, 0))

        # Check if the request path is for API endpoints (e.g., messages, conversations)
        # You might want to adjust this regex based on your URL patterns
        # For simplicity, let's assume '/api/' paths are what we want to restrict
        if request.path.startswith('/api/'): # or re.match(r'^/api/(messages|conversations)/', request.path)
            if is_restricted:
                return HttpResponseForbidden("Access to chat is restricted between 9 PM and 6 AM.")

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware to detect and block offensive language in messages.
    Also implements a rate limit for messages based on IP address.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_messages = 5
        self.rate_limit_window_minutes = 1
        # offensive_words = ['badword1', 'badword2', 'offensive_term'] # Example list
        # self.offensive_patterns = [re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE) for word in offensive_words]

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/api/messages/'):
            # Task 3: Offensive Language / Rate Limiting
            ip_address = self._get_client_ip(request)

            with ip_request_data_lock:
                if ip_address not in ip_request_data:
                    ip_request_data[ip_address] = []

                # Clean up old requests outside the time window
                now = datetime.now()
                ip_request_data[ip_address] = [
                    timestamp for timestamp in ip_request_data[ip_address]
                    if now - timestamp < timedelta(minutes=self.rate_limit_window_minutes)
                ]

                # Check rate limit
                if len(ip_request_data[ip_address]) >= self.rate_limit_messages:
                    return HttpResponseForbidden(
                        f"Rate limit exceeded: You can send only {self.rate_limit_messages} messages "
                        f"per {self.rate_limit_window_minutes} minute."
                    )

                # If not rate-limited, add current request timestamp
                ip_request_data[ip_address].append(now)

            # Offensive Language Check (Optional - if you have a list of offensive words)
            # This task description is a bit ambiguous, it says "Detect and Block offensive Language"
            # but then "Implement middleware that limits the number of chat messages...".
            # The name "OffensiveLanguageMiddleware" suggests blocking offensive words,
            # but the instructions mostly describe rate limiting.
            # If you *do* want to block offensive words, uncomment and populate self.offensive_patterns.
            # try:
            #     # Assuming message content is in request.data['content']
            #     message_content = request.POST.get('content', '') or request.data.get('content', '')
            #     for pattern in self.offensive_patterns:
            #         if pattern.search(message_content):
            #             return HttpResponseForbidden("Offensive language detected. Your message cannot be sent.")
            # except Exception as e:
            #     # Handle cases where request.data might not be parsed yet or content is missing
            #     print(f"Error checking offensive language: {e}")
            #     pass # Let the request proceed if parsing fails or content is not found easily


        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware(MiddlewareMixin):
    """
    Middleware to enforce chat user role permissions.
    Only allows 'admin' or 'moderator' roles to access specific actions/paths.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that require specific roles
        # Adjust these regex patterns to match your admin/moderator-specific API endpoints
        self.restricted_paths_for_roles = [
            re.compile(r'^/admin/'), # Django Admin site
            # re.compile(r'^/api/moderation/'), # Example: A hypothetical moderation API endpoint
            # re.compile(r'^/api/users/(?P<pk>\d+)/delete/$'), # Example: Delete user endpoint
        ]

    def __call__(self, request):
        # Apply this check only if the user is authenticated and for specific paths
        if request.user.is_authenticated:
            for pattern in self.restricted_paths_for_roles:
                if pattern.match(request.path):
                    # Check if the user is an admin or moderator (assuming roles are handled by user flags or groups)
                    # For simplicity, let's use is_staff and is_superuser.
                    # If you have a custom User model with a 'role' field or groups, adjust this.
                    if not (request.user.is_staff or request.user.is_superuser):
                        # Example: If you have a 'role' field on your User model
                        # if not (request.user.role == 'admin' or request.user.role == 'moderator'):
                        return HttpResponseForbidden("You do not have the necessary permissions to access this resource.")
                    break # Break if a matching restricted path is found and role check is done

        response = self.get_response(request)
        return response
