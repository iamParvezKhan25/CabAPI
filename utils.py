import math
import random

from django.core.mail import EmailMessage
# from rest_framework.renderers import JSONRenderer

__all__ = ['GenerateOtp']


class GenerateOtp:

    @staticmethod
    def generateOTP():
        # Declare a digits variable
        # which stores all digits
        digits = "0123456789"
        OTP = ""

        # length of password can be chaged
        # by changing value in range
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]
        return OTP


class Util:

    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'],
                             body=data['email_body'],
                             to=[data['to_email']])
        email.send()

# 
# class CustomRenderer(JSONRenderer):
#     """
#     defined custom response format for APIs
#     code [0, 1, 2]
#     message[success, not found, error]
#     data
#     """
# 
#     def render(self, data, accepted_media_type=None, renderer_context=None):
#         status_code = renderer_context['response'].status_code
#         print(data)
# 
#         response_data = {
#             200: {
#                 "code": 1,
#                 "message": "success",
#                 "data": data
#             },
#             201: {
#                 "code": 1,
#                 "message": "success",
#                 "data": "Created success"
#             },
#             204: {
#                 "code": 1,
#                 "message": "success",
#                 "data": "No Content"
#             },
#             404: {
#                 "code": 2,
#                 "message": "Not Found",
#             }
#         }
#         response = response_data.get(status_code, {
#             "code": 0,
#             "message": data,
#         })
# 
#         return super().render(response, accepted_media_type, renderer_context)
