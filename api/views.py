from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q
from collections import OrderedDict
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import os
from django.http import FileResponse, HttpResponse
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
    JWTTokenUserAuthentication,
)
from django.contrib.auth.decorators import login_required
import hashlib
import urllib.parse

from .serializers import *
from . import status_http
from .models import *

#


def create_url_signature(url, secret_key):
    url_with_secret = url + secret_key
    sha256_hash = hashlib.sha256(url_with_secret.encode()).hexdigest()
    signed_url = url + "?signature=" + sha256_hash
    return signed_url


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
# @login_required
def protected_media_view(request, path):
    media_file_path = os.path.join(path, "")
    print("signed_url: ", media_file_path)
    return FileResponse(
        open(media_file_path, "rb"), content_type="application/octet-stream"
    )


# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# # @login_required
# def protected_media_view(request, subpath, filename):
#     # Build the full path to the media file
#     pathTemp = "/documents/document_library/"
#     # pathTemp = "/documents/document_library/video_khoa_1"
#     media_file_path = os.path.join(settings.MEDIA_ROOT + pathTemp + subpath, filename)
#     # print("protected_media_view: ", media_file_path)
#     # Serve the file using Django's FileResponse
#     # secret_key = "your_secret_key"
#     # signed_url = create_url_signature(media_file_path, secret_key)
#     # print("signed_url: ", signed_url)
#     return FileResponse(open(media_file_path, 'rb'), content_type='application/octet-stream')


def textfile_view(request, filename):
    # Construct the full path to the text file
    file_path = os.path.join(settings.MEDIA_ROOT, "textfiles", filename)

    # Check if the file exists
    if os.path.exists(file_path):
        # Serve the file as a response
        with open(file_path, "rb") as file:
            file_content = file.read()
            response = FileResponse(file_content)
        return response

    # File not found, you can handle this case as needed
    return HttpResponse("File not found", status=404)


# Profile ==========================================================


class ProfileMVS(viewsets.ModelViewSet):
    serializer_class = CareerProfileUpdateAuthenticationSerializer

    #
    @action(
        methods=["POST"],
        detail=False,
        url_path="profile_check_exist_api",
        url_name="profile_check_exist_api",
    )
    def profile_check_exist_api(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data = {}
                data["is_exist"] = serializer.check_is_exist(request)
                data["is_sub_mentor"] = serializer.check_is_leader_support_course(
                    request
                )
                data["is_mentor"] = serializer.check_is_mentor(request)
                data["is_student"] = serializer.check_is_student(request)
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("ProfileMVS_profile_check_exist_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="profile_add_api",
        url_name="profile_add_api",
    )
    def profile_add_api(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                model = serializer.add(request)
                # print("profile_add_api: ", model)
                if model:
                    data = {}
                    data["message"] = "Add successfully!"
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("ProfileMVS_profile_add_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


# class UploadAvatarUserMVS(viewsets.ModelViewSet):
#     serializer_class = UploadAvatarUserSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser)

#     @action(methods=["PATCH"], detail=False, url_path="upload_avatar_user_api", url_name="upload_avatar_user_api")
#     def upload_avatar_user_api(self, request, *args, **kwargs):
#         try:
#             serializer = self.serializer_class(data=request.data)
#             if serializer.is_valid():
#                 result = serializer.update_avatar(request)
#                 if result:
#                     return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             print("upload_avatar_user_api: ", error)
#         return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def get_profile_view(request):
    if request.method == "GET":
        data = {}
        data["email"] = request.user.email
        user = User.objects.get(email=request.user.email)
        data["first_name"] = user.first_name
        data["last_name"] = user.last_name
        data["id"] = user.id
        groups = Group.objects.filter(user=request.user)
        groups_ = []
        for g in groups:
            groups_.append(g.name)
        data["groups"] = groups_
        #
        permissions = Permission.objects.filter(
            Q(user=user) | Q(group__user=user)
        ).all()
        permissions_user = []
        for p in permissions:
            permissions_user.append(p.name)
        data["permissions"] = permissions_user
        #
        profile = {}
        try:
            qsProfile = CareerProfile.objects.get(pk=user.id)
            profile = UserCareerProfileSerializer(qsProfile).data
        except Exception as error:
            print("get_profile_view_error: ", error)
        data["profile"] = profile
        #
        # setting = Setting.objects.first()
        # setting_serializer = SettingOnlyBanClickMouseSerializer(setting, many=False)
        # data['ban_click_mouse'] = setting_serializer.data["ban_click_mouse"]

        return Response(data, status=status.HTTP_200_OK)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def update_user_profile_view(request):
    if request.method == "PATCH":
        serializer = UpdateCareerProfileSerializer(
            data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            try:
                serializer.save()
                data["email"] = request.data["email"]
                data["message"] = "Update profile successfully!"
                return Response(data, status=status.HTTP_200_OK)
            except:
                return Response(serializer.errors, status=423)
        return Response(serializer.errors, status=425)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def update_user_view(request):
    if request.method == "PATCH":
        serializer = UpdateUserSerializer(data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            try:
                serializer.save()
                data["email"] = request.data["email"]
                data["message"] = "Update profile successfully!"
                return Response(data, status=status.HTTP_200_OK)
            except:
                return Response(serializer.errors, status=423)
        return Response(serializer.errors, status=425)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def change_password_view(request):
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            try:
                if not serializer.old_password_validate():
                    data["email"] = request.data["email"]
                    data["message"] = "Old password is incorrect"
                    return Response(
                        data, status=status_http.HTTP_ME_454_OLD_PASSWORD_IS_INCORRECT
                    )
                serializer.update()
                data["email"] = request.data["email"]
                data["message"] = "Change password successfully"
                return Response(data, status=status.HTTP_200_OK)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class HistoryLogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        next_page = previous_page = None
        if self.page.has_next():
            next_page = self.page.next_page_number()
        if self.page.has_previous():
            previous_page = self.page.previous_page_number()
        return Response(
            {
                "totalRows": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page": self.page.number,
                "next_page": next_page,
                "previous_page": previous_page,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )


class HistoryLogMVS(viewsets.ModelViewSet):
    serializer_class = HistoryLogSerializer
    pagination_class = HistoryLogPagination
    permission_classes = [IsAuthenticated]

    @action(
        methods=["GET"],
        detail=False,
        url_path="history_log_get_all_api",
        url_name="history_log_get_all_api",
    )
    def history_log_get_all_api(self, request, *args, **kwargs):
        queryset = HistoryLog.objects.all().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Authentication ==========================================================


@api_view(["POST"])
def reset_password_view(request):
    if request.method == "POST":
        serializer = ResetPasswordSerializer(data=request.data)
        data = {}
        refresh_token = request.data["refresh_token"]
        if serializer.is_valid():
            if not serializer.is_refresh_token_valid(refresh_token):
                data["message"] = (
                    "Token is incorrect or expired or the email does not exist!"
                )
                return Response(
                    data, status=status_http.HTTP_ME_455_TOKEN_INCORRECT_OR_EXPIRED
                )
            serializer.change_password()
            data["message"] = "Reset password successfully!"
            return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def active_account_view(request):
    if request.method == "POST":
        serializer = ActiveAccountSerializer(data=request.data)
        data = {}
        # access_token = request.headers['x-access-token']
        access_token = request.data["access_token"]
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data["message"] = "Email does not exist!"
                return Response(
                    data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST
                )
            if serializer.is_account_active():
                data["message"] = "The account is activated already. Please login!"
                return Response(
                    data, status=status_http.HTTP_ME_453_ACCOUNT_IS_ACTIVATED
                )
            if not serializer.is_token_valid(access_token):
                data["message"] = "Token is incorrect or expired!"
                return Response(
                    data, status=status_http.HTTP_ME_455_TOKEN_INCORRECT_OR_EXPIRED
                )
            serializer.save()
            data["email"] = request.data["email"]
            data["message"] = "Activate account successfully!"
            return Response(data, status=status.HTTP_200_OK)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def resend_link_activation_view(request):
    if request.method == "POST":
        serializer = ResendActivationLinkSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data["message"] = "Email does not exist!"
                return Response(
                    data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST
                )
            if serializer.is_account_active():
                data["message"] = "The account is activated already. Please login!"
                return Response(
                    data, status=status_http.HTTP_ME_453_ACCOUNT_IS_ACTIVATED
                )
            if serializer.send_mail():
                data["message"] = "Send an activation link to your email successfully!"
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def forgot_password_view(request):
    if request.method == "POST":
        serializer = ForgotPasswordSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if not serializer.is_email_exist():
                data["message"] = "Email does not exist!"
                return Response(
                    data, status=status_http.HTTP_ME_451_EMAIL_DOES_NOT_EXIST
                )
            if not serializer.is_account_active():
                data["message"] = "The account is not activated. Please active it!"
                return Response(
                    data, status=status_http.HTTP_ME_452_ACCOUNT_IS_NOT_ACTIVATED
                )
            if serializer.send_mail():
                data["message"] = "Send an activation link to your email successfully!"
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def registration_view(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            if serializer.is_email_exist():
                data["message"] = "Email exist!"
                return Response(data, status=status_http.HTTP_ME_450_EMAIL_EXIST)
            user = serializer.save()
            data["message"] = (
                "Registered successfully! A mail sent to your mailbox for activation account."
            )
            data["email"] = user.email
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


# ===========================================================


class GoogleView(APIView):
    def post(self, request):

        s = Setting.objects.first()
        if s and s.is_lock_login:
            content = {"message": "Không thể đăng nhập lúc này"}
            return Response(content)

        # email = request.data.get("email")
        # print("GoogleView_email: ", email)
        payload = {
            "access_token": request.data.get("token_google")
        }  # validate the token
        r = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", params=payload
        )
        data = json.loads(r.text)

        if "error" in data:
            content = {
                "message": "wrong google token / this google token is already expired."
            }
            return Response(content)

        # print("GoogleView_data: ", data)

        email = data["email"]
        # create user if not exist
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print("GoogleView_User.DoesNotExist")
            # token_google = request.data.get("token_google")
            # avatar = request.data.get("imageUrl")
            first_name = request.data.get("givenName")
            last_name = request.data.get("familyName")
            user = User()
            user.username = email
            # provider random default password
            user.password = make_password(
                BaseUserManager().make_random_password())
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            #
            member_group = Group.objects.get(
                name=settings.GROUP_NAME["MEMBER"])
            member_group.user_set.add(user)
            #
            Profile.objects.create(user=user, phone="")

        # generate token without username & password
        token = RefreshToken.for_user(user)
        response = {}
        response["access"] = str(token.access_token)
        response["refresh"] = str(token)
        return Response(response)


class CareerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        next_page = previous_page = None
        if self.page.has_next():
            next_page = self.page.next_page_number()
        if self.page.has_previous():
            previous_page = self.page.previous_page_number()
        return Response(
            {
                "totalRows": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page": self.page.number,
                "next_page": next_page,
                "previous_page": previous_page,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )


class ImageLibraryCategoryViewSet(viewsets.ModelViewSet):
    queryset = ImageLibraryCategory.objects.all()
    serializer_class = ImageLibraryCategorySerializer


class ImageLibraryViewSet(viewsets.ModelViewSet):
    queryset = ImageLibrary.objects.all()
    serializer_class = ImageLibrarySeriProfileisalizer


class CareerProfileViewSet(viewsets.ModelViewSet):
    queryset = CareerProfile.objects.all()
    serializer_class = CareerProfileSerializer2
    # permission_classes = [IsAuthenticated]

    # @action(methods=['PATCH'], detail=True, url_path='update-user-profile', url_name='update-user-profile')
    # def update_user_profile(self, request):
    #     try:
    #         serializers =
    #     except Exception as error :
    #         pass


class UserCareerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserCareerProfileSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="get_all_user_profile",
        url_name="get_all_user_profile",
    )
    def get_all_user_profile(self, request):
        queryset = CareerProfile.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="get_user_by_token")
    def get_user_by_token(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="check_and_create")
    def check_and_create(self, request):
        try:
            email = request.data.get("email")
            username = request.data.get("username")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User()
                user.username = username
                user.password = make_password(
                    BaseUserManager().make_random_password())
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
            token = RefreshToken.for_user(user)
            profile, created = CareerProfile.objects.get_or_create(
                user_id=user, address="da nang"
            )
            # Account.objects.create(user=user, account_type='google', account_identifier='')
            serializer = self.get_serializer(profile)
            return Response(
                {
                    "user_career": serializer.data,
                    "access_token_jwt": str(token.access_token),
                    "refresh_token_jwt": str(token),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            print("check_and_create_error: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class UploadAvatarCareerProfile(viewsets.ModelViewSet):
    serializer_class = UploadAvatarCareerProfileSerializer
    # permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="upload_avatar_career_profile_api",
        url_name="upload_avatar_career_profile_api",
    )
    def upload_avatar_career_profile_api(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                result = serializer.update_avatar(request)
                if result:
                    serializer = UserCareerProfileSerializer(result)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("upload_avatar_user_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class CareerCategoryLevel1MVS(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CareerCategoryLevel1Serializer
    pagination_class = CareerPagination

    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_get_all_api",
        url_name="career_category_get_all_api",
    )
    def career_category_get_all_api(self, request, *args, **kwargs):
        queryset = CareerCategoryLevel1.objects.order_by("-create_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_get_by_id",
        url_name="career_category_get_by_id",
    )
    def career_category_get_by_id_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel1.objects.get(id=id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CareerCategoryLevel1.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_get_by_id_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="career_category_create_api",
        url_name="career_category_create_api",
    )
    def career_category_create_api(self, request, *args, **kwargs):
        try:
            serializer = CareerCategoryLevel1Serializer(data=request.data)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.add()
                if model:
                    data = {}
                    data["message"] = "Add successfully!"
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response(
                {"message: ": "Add failed!"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            print("career_category_create_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PUT"],
        detail=False,
        url_path="career_category_update_api",
        url_name="career_category_update_api",
    )
    def career_category_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel1.objects.get(id=id)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel1.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="career_category_partial_update_api",
        url_name="career_category_partial_update_api",
    )
    def career_category_partial_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel1.objects.get(id=id)
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel1.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_partial_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["DELETE"],
        detail=False,
        url_path="career_category_delete_api",
        url_name="career_category_delete_api",
    )
    def career_category_delete_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel1.objects.get(id=id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CareerCategoryLevel1.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_delete_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class CareerCategoryLevel2MVS(viewsets.ModelViewSet):
    queryset = CareerCategoryLevel2.objects.all()
    serializer_class = CareerCategoryLevel2Serializer
    pagination_class = CareerPagination

    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_get_all_api",
        url_name="career_category_get_all_api",
    )
    def career_category_get_all_api(self, request, *args, **kwargs):
        queryset = CareerCategoryLevel2.objects.order_by("-create_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_get_by_id",
        url_name="career_category_get_by_id",
    )
    def career_category_get_by_id_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2.objects.get(id=id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CareerCategoryLevel2.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_get_by_id_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="career_category_create_api",
        url_name="career_category_create_api",
    )
    def career_category_create_api(self, request, *args, **kwargs):
        try:
            serializer = CareerCategoryLevel2Serializer(data=request.data)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.add()
                if model:
                    data = {}
                    data["message"] = "Add successfully!"
                    return Response(data, status=status.HTTP_201_CREATED)

            return Response(
                {"error: ": "Add failed!"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            print("career_category_create_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PUT"],
        detail=False,
        url_path="career_category_update_api",
        url_name="career_category_update_api",
    )
    def career_category_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2.objects.get(id=id)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel2.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="career_category_partial_update_api",
        url_name="career_category_partial_update_api",
    )
    def career_category_partial_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2.objects.get(id=id)
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if serializer.is_valid():
                if serializer.is_name_exist():
                    return Response(
                        {"details: ": "Name exists"},
                        status=status_http.HTTP_ME_463_NAME_EXIST,
                    )
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel2.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_partial_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["DELETE"],
        detail=False,
        url_path="career_category_delete_api",
        url_name="career_category_delete_api",
    )
    def career_category_delete_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2.objects.get(id=id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CareerCategoryLevel2.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_delete_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class RecruitmentPostMVS(viewsets.ModelViewSet):
    serializer_class = RecruitmentPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CareerPagination

    @action(
        methods=["GET"],
        detail=False,
        url_path="recruitment_post_get_all_api",
        url_name="recruitment_post_get_all_api",
    )
    def recruitment_post_get_all_api(self, request):
        queryset = RecruitmentPost.objects.order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="recruitment_post_get_by_id",
        url_name="recruitment_post_get_by_id",
    )
    def recruitment_post_get_by_id_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("recruitment_post_get_by_id_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="recruitment_post_create_api",
        url_name="recruitment_post_create_api",
    )
    def recruitment_post_create_api(self, request, *args, **kwargs):
        try:
            serializer = RecruitmentPostSerializer(data=request.data)
            if serializer.is_valid():
                model = serializer.add()
                if model:
                    data = {}
                    data["message"] = "Add successfully!"
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response(
                {"error: ": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            print("recruitment_post_create_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PUT"],
        detail=False,
        url_path="recruitment_post_update_api",
        url_name="recruitment_post_update_api",
    )
    def recruitment_post_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("recruitment_post_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="recruitment_post_partial_update_api",
        url_name="recruitment_post_partial_update_api",
    )
    def recruitment_post_partial_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if serializer.is_valid():
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("recruitment_post_partial_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["DELETE"],
        detail=False,
        url_path="recruitment_post_delete_api",
        url_name="recruitment_post_delete_api",
    )
    def recruitment_post_delete_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = RecruitmentPost.objects.get(id=id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("recruitment_post_delete_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class CareerCategoryLevel2_RecruitmentPostMVS(viewsets.ModelViewSet):
    serializer_class = CareerCategoryLevel2_RecruitmentPost_Serializers
    pagination_class = CareerPagination
    permission_classes = [IsAuthenticated]
    
    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api",
        url_name="career_category_recruitment_post_get_all_api",
    )
    def career_category_recruitment_post_get_all_api_get_all_api(self, request):
        queryset = CareerCategoryLevel2_RecruitmentPost.objects.order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api_get_by_id",
        url_name="career_category_recruitment_post_get_all_api_get_by_id",
    )
    def career_category_recruitment_post_get_all_api_get_by_id_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2_RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CareerCategoryLevel2_RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_recruitment_post_get_all_api_get_by_id_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api_create_api",
        url_name="career_category_recruitment_post_get_all_api_create_api",
    )
    def career_category_recruitment_post_get_all_api_create_api(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                model = serializer.add()
                if model:
                    data = {}
                    data["message"] = "Add successfully!"
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response(
                {"error: ": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            print("career_category_recruitment_post_get_all_api_create_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PUT"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api_update_api",
        url_name="career_category_recruitment_post_get_all_api_update_api",
    )
    def career_category_recruitment_post_get_all_api_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2_RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel2_RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_recruitment_post_get_all_api_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api_partial_update_api",
        url_name="career_category_recruitment_post_get_all_api_partial_update_api",
    )
    def career_category_recruitment_post_get_all_api_partial_update_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2_RecruitmentPost.objects.get(id=id)
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if serializer.is_valid():
                model = serializer.save()
                if model:
                    data = {}
                    data["message"] = "Update successfully!"
                    return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerCategoryLevel2_RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_recruitment_post_get_all_api_partial_update_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["DELETE"],
        detail=False,
        url_path="career_category_recruitment_post_get_all_api_delete_api",
        url_name="career_category_recruitment_post_get_all_api_delete_api",
    )
    def career_category_recruitment_post_get_all_api_delete_api(self, request, *args, **kwargs):
        try:
            id = request.query_params.get("id")
            instance = CareerCategoryLevel2_RecruitmentPost.objects.get(id=id)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CareerCategoryLevel2_RecruitmentPost.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print("career_category_recruitment_post_get_all_api_delete_api: ", error)
        return Response({"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
