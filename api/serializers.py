from django.contrib.auth.models import User, Group, Permission
from django.core.validators import EmailValidator
from django.db.models import fields
from django.utils.crypto import get_random_string
from requests.api import request
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import socket
import calendar
import time
from getmac import get_mac_address as gma
from user_agents import parse
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from datetime import timedelta, datetime
from django.utils.text import slugify
from api.models import *

# from api.submodels.models_student import StudentMe
from unidecode import unidecode


def getOriginalRefreshToken(refresh_token):
    try:
        original_string = ""
        temp_string = refresh_token.split("@%.!")
        if len(temp_string) > 0:
            if len(str(temp_string[0])) > 0:
                return ""
            original_string = str(temp_string[1])
        return original_string
    except:
        return ""


def getUserFromRefreshToken(self, refresh_token):
    try:
        refresh_token = RefreshToken(refresh_token)
        # print("refresh_token: ", refresh_token)
        user_id = refresh_token["user_id"]
        user = User.objects.get(pk=user_id)
        return user
    except:
        return None


def getUserFromAccessToken(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token["user_id"]
        user = User.objects.get(pk=user_id)
        return user
    except:
        return None


def _is_token_valid(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token["user_id"]
        User.objects.get(email=self.validated_data["email"], id=user_id)
        return True
    except:
        return False


def _token_get_exp(access_token):
    try:
        access_token = AccessToken(access_token)
        return access_token["exp"]
    except Exception as error:
        print("===_token_get_exp", error)
        return None


class ImageLibraryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLibraryCategory
        fields = "__all__"


class ImageLibrarySeriProfileisalizer(serializers.ModelSerializer):
    class Meta:
        model = ImageLibrary
        fields = "__all__"


class HistoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryLog
        fields = "__all__"


# Authentication ================================================================


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("name",)


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "name",
            "permissions",
        )


class CreateAccessTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def is_account_active(self):
        try:
            user = User.objects.get(email=self.validated_data["email"], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data["email"])
            return True
        except:
            return False

    def get_user(self):
        try:
            return User.objects.get(email=self.validated_data["email"])
        except:
            return None


class ActiveAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def is_account_active(self):
        try:
            user = User.objects.get(email=self.validated_data["email"], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data["email"])
            return True
        except:
            return False

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.is_active = True
        user.save()
        return user

    def is_token_valid(self, access_token):
        return _is_token_valid(self, access_token)


class ResendActivationLinkSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def is_account_active(self):
        try:
            user = User.objects.get(email=self.validated_data["email"], is_active=True)
            return True
        except:
            return False

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data["email"])
            return True
        except:
            return False

    def send_mail(self):
        user = User.objects.get(email=self.validated_data["email"])
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        link_active = settings.FRONTEND_SITE_URL_ACTIVE_ACCOUNT + "".join(access_token)
        message = render_to_string(
            "api/mail/resend_link_active_account.html",
            {"link_active": link_active, "email_title": settings.EMAIL_TITLE},
        )
        send = EmailMessage(
            settings.EMAIL_TITLE,
            message,
            from_email=settings.EMAIL_FROM,
            to=[self.validated_data["email"]],
        )
        send.content_subtype = "html"
        send.send()
        return True


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    school_domain = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ["email", "school_domain"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def is_account_active(self):
        try:
            User.objects.get(email=self.validated_data["email"], is_active=True)
            return True
        except:
            return False

    # def is_email_exist(self):
    #     try:
    #         email = self.validated_data["email"]
    #         school_domain = self.validated_data["school_domain"]
    #         User.objects.get(email=email)
    #         checkSchoolValid = StudentMe.objects.filter(
    #             email=email, domain_school=school_domain
    #         ).count()
    #         if checkSchoolValid == 0:
    #             return False
    #         return True
    #     except:
    #         return False

    def send_mail(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        refresh = RefreshToken.for_user(user)
        from_time = datetime.utcnow()
        expiration_time = timedelta(minutes=15)
        refresh.set_exp(from_time=from_time, lifetime=expiration_time)
        refresh_token = str(refresh)
        refresh_token_fake = "@%.!" + refresh_token
        # print("refresh_token: ", refresh_token_fake)
        # print("expiration_time: ", refresh)
        # link_active = settings.FRONTEND_SITE_URL_RESET_PASSWORD + \
        #     ''.join(access_token)
        message = render_to_string(
            "api/mail/forgot_password.html",
            {"email_title": settings.EMAIL_TITLE, "code": refresh_token_fake},
        )
        send = EmailMessage(
            settings.EMAIL_TITLE,
            message,
            from_email=settings.EMAIL_FROM,
            to=[self.validated_data["email"]],
        )
        send.content_subtype = "html"
        send.send()
        #
        return True


def _current_user(self):
    request = self.context.get("request", None)
    if request:
        return request.user
    return False


def visitor_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class MySimpleJWTSerializer(TokenObtainPairSerializer):
    my_ip_address = "0.0.0.0"
    myRequest = None

    @classmethod
    def get_token(cls, user):
        # print("user: ", user)
        token = super().get_token(user)
        user_obj = User.objects.get(username=user)
        #
        token["email"] = user_obj.email

        access_token = str(token.access_token)
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        # ip_address = str(MySimpleJWTSerializer.my_ip_address)
        mac_address = gma()
        # print("===444", hostname)
        # print("===555", ip_address)
        # print("===666", mac_address)
        # print("===my_ip_address", MySimpleJWTSerializer.my_ip_address)

        # request = cls.context("request", None)
        # #
        sessionToken = SessionToken.objects.filter(user=user).count()
        if sessionToken == 0:
            sessionToken = SessionToken.objects.get_or_create(
                user=user,
                token=access_token,
                hostname=hostname,
                ip_address=MySimpleJWTSerializer.my_ip_address,
                mac_address=mac_address,
            )
        else:
            sessionToken = SessionToken.objects.get(user=user)
            token_temp = sessionToken.token
            mac_address_temp = sessionToken.mac_address
            ip_address_temp = sessionToken.ip_address

            #
            exp = _token_get_exp(token_temp)
            if exp is not None:
                ts_now = calendar.timegm(time.gmtime())
                # print("===3 : {exp}, {ts_now}", exp, ts_now)
                if ts_now < exp:
                    pass
                    # print("===Exp not end", exp)
                    # if ip_address_temp != MySimpleJWTSerializer.my_ip_address:
                    #     return None
                # else:
                #     print("===42", ts_now)
            else:
                SessionToken.objects.filter(user=user).update(
                    token=access_token,
                    hostname=hostname,
                    ip_address=MySimpleJWTSerializer.my_ip_address,
                    mac_address=mac_address,
                )
                # print("===Exp end")
        #
        # try:
        #     user_agent = MySimpleJWTSerializer.myRequest.user_agent
        #     browser_name = user_agent.browser.family
        #     is_pc = user_agent.is_pc
        #     is_mobile = user_agent.is_mobile
        #     is_tablet = user_agent.is_tablet
        #     device = ""
        #     if is_pc == True:
        #         device = "PC"
        #     elif is_mobile == True:
        #         device = "Mobile"
        #     elif is_tablet == True:
        #         device = "Tablet"
        #     HistoryLog.objects.create(user=user, hostname=hostname, ip_address=MySimpleJWTSerializer.my_ip_address,
        #                               mac_address=mac_address, browser=browser_name, device=device)
        # except Exception as err:
        #     print("HistoryLog: ", str(err))
        #     pass
        return token

    # def validate(self, attrs):
    #     credentials = {"username": "", "password": attrs.get("password")}
    #     # print("school_domain: ", attrs)
    #     #
    #     school_domain = ""
    #     email = ""
    #     username = attrs.get("username").strip()
    #     username_temp = username
    #     username_temp = username_temp.split(":google:email:")
    #     if len(username_temp) > 1:
    #         email = username_temp[0]
    #         school_domain = username_temp[1]
    #         checkSchoolValid = StudentMe.objects.filter(
    #             email=email, domain_school=school_domain
    #         ).count()
    #         # print("checkSchoolValid: ", email)
    #         if checkSchoolValid == 0:
    #             return super().validate(credentials)
    #     else:
    #         email = username
    #     #
    #     # user_obj = User.objects.filter(email=attrs.get("username")).first(
    #     # ) or User.objects.filter(username=attrs.get("username")).first()
    #     user_obj = (
    #         User.objects.filter(email=email).first()
    #         or User.objects.filter(username=email).first()
    #     )
    #     if user_obj:
    #         credentials["username"] = user_obj.username
    #     # request = self.context.get('request', None)
    #     # print("===validate", visitor_ip_address(request))
    #     # MySimpleJWTSerializer.myRequest = request
    #     # MySimpleJWTSerializer.my_ip_address = visitor_ip_address(request)
    #     return super().validate(credentials)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MySimpleJWTSerializer


# ==========================================

# https://stackoverflow.com/questions/54544978/customizing-jwt-response-from-django-rest-framework-simplejwt
# class LoginGoogleSerializer(TokenObtainPairSerializer):
#     my_ip_address = "0.0.0.0"
#     myRequest = None

#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         user_obj = User.objects.get(username=user)
#         token['email'] = user_obj.email
#         return token

#     def validate(self, attrs):
#         print("validate333: ", attrs)
#         # credentials = {
#         #     'username': '',
#         #     'password': attrs.get("password")
#         # }
#         # user_obj = User.objects.filter(email=attrs.get("username")).first(
#         # ) or User.objects.filter(username=attrs.get("username")).first()
#         # if user_obj:
#         #     credentials['username'] = user_obj.username

#         # token_google = attrs.get("token")
#         email = attrs.get("email")
#         firstName = attrs.get("givenName")
#         lastName = attrs.get("familyName")
#         avatar = attrs.get("imageUrl")

#         # create user if not exist
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             user = User()
#             user.username = email
#             # provider random default password
#             user.password = make_password(BaseUserManager().make_random_password())
#             user.email = email
#             user.save()

#         request = self.context.get('request', None)
#         print("===validate_LoginGoogleSerializer", visitor_ip_address(request))
#         LoginGoogleSerializer.myRequest = request
#         LoginGoogleSerializer.my_ip_address = visitor_ip_address(request)
#         return user


# class LoginGoogleView(TokenObtainPairView):
#     serializer_class = LoginGoogleSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name"]


class UserCareerProfileSerializer(serializers.ModelSerializer):
    user_id = UserSerializer()

    class Meta:
        model = CareerProfile
        fields = ["address", "phone", "avatar", "create_at", "update_at", "user_id"]


class UploadAvatarCareerProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField()
    user_id = serializers.IntegerField()

    class Meta:
        model = CareerProfile
        fields = ["avatar", "user_id"]

    def update_avatar(self, request):
        image_library_category = ImageLibraryCategory.objects.get(name="avatar")
        avatar = ImageLibrary(
            title="",
            image=self.validated_data["avatar"],
            image_library_category=image_library_category,
        )
        avatar.save()
        try:

            user_id = self.validated_data["user_id"]
            model = CareerProfile.objects.get(pk=user_id)
            # storage, path = model.avatar.image.storage, model.avatar.image.path
            model.avatar = avatar
            model.save()
            # if storage.exists(path):
            #     if "avatar_default.png" not in path:
            #         storage.delete(path)
            return model
        except Exception as error:
            print("UploadAvatarCareerProfileSerializer_update_avatar_error: ", error)
            return None


class CareerProfileUpdateAuthenticationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)

    class Meta:
        model = CareerProfile
        fields = ["phone", "email"]
        # extra_fields = ['email']

    def check_is_exist(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(user__email=email)
        if len(filterExist) > 0:
            return True
        return False

    def check_is_teacher_mentor(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(
            user__email=email, is_teacher_mentor=True
        )
        if len(filterExist) > 0:
            return True
        return False

    def check_is_college_student(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(
            user__email=email, is_college_student=True
        )
        if len(filterExist) > 0:
            return True
        return False

    def check_is_parent(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(user__email=email, is_parent=True)
        if len(filterExist) > 0:
            return True
        return False

    def check_is_company(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(user__email=email, is_company=True)
        if len(filterExist) > 0:
            return True
        return False

    def check_is_student(self, request):
        email = self.validated_data["email"]
        filterExist = CareerProfile.objects.filter(
            user__email=email,
            is_teacher_mentor=False,
            is_college_student=False,
            is_parent=False,
            is_company=False,
        )
        if len(filterExist) > 0:
            return True
        return False

    def add(self, request):
        try:
            phone = self.validated_data["phone"]
            email = self.validated_data["email"]
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")

            user = User()
            user.username = email
            # provider random default password
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            member_group = Group.objects.get(name=settings.GROUP_NAME["MEMBER"])
            member_group.user_set.add(user)

            CareerProfile.objects.create(user=user, phone=phone)

            return True
        except Exception as error:
            print("ProfileSerializer_add_error: ", error)
            return None


class CareerProfileSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CareerProfile
        fields = [
            "address",
            "gender",
            "phone",
            "facebook",
            # "avatar",
            # "count_change_password",
            # "is_teacher_mentor"
        ]


class UpdateCareerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    career_profile = CareerProfileSerializer2()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "career_profile"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.save()
        career_profile = CareerProfile.objects.get(pk=user.id)
        career_profile_data = self.validated_data["career_profile"]
        career_profile.phone = career_profile_data["phone"]
        career_profile.address = career_profile_data["address"]
        career_profile.gender = career_profile_data["gender"]
        career_profile.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        extra_kwargs = {
            "email": {"validators": [EmailValidator]},
        }

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "old_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "old_password": {"write_only": True},
            "email": {"validators": [EmailValidator]},
        }

    def validate(self, data):
        if len(data["old_password"]) < 5:
            raise serializers.ValidationError(
                {"message": "Password must be at least 5 characters."}
            )
        if len(data["password"]) < 5:
            raise serializers.ValidationError(
                {"message": "Password must be at least 5 characters."}
            )
        return data

    def old_password_validate(self):
        user = User.objects.get(email=self.validated_data["email"])
        if not user.check_password(self.validated_data["old_password"]):
            return False
        return True

    def update(self):
        user = User.objects.get(email=self.validated_data["email"])
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        try:
            profile = CareerProfile.objects.get(pk=user)
            profile.count_change_password += 1
            profile.save()
        except Exception as error:
            print("ProfileSerializer_update_count_change_pass_error: ", error)
        return user


class ResetPasswordSerializer(serializers.ModelSerializer):
    refresh_token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["password", "refresh_token"]

    # def is_token_valid(self, access_token):
    #     try:
    #         access_token = AccessToken(access_token)
    #         user_id = access_token["user_id"]
    #         User.objects.get(id=user_id)
    #         return True
    #     except:
    #         return False

    def is_refresh_token_valid(self, refresh_token):
        try:
            refresh_token = getOriginalRefreshToken(refresh_token)
            refresh_token = RefreshToken(refresh_token)
            user_id = refresh_token["user_id"]
            User.objects.get(id=user_id)
            return True
        except:
            return False

    def change_password(self):
        refresh_token = self.validated_data["refresh_token"]
        password = self.validated_data["password"]
        refresh_token = getOriginalRefreshToken(refresh_token)
        user = getUserFromRefreshToken(self, refresh_token=refresh_token)
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        try:
            profile = CareerProfile.objects.get(pk=user)
            profile.count_change_password += 1
            profile.save()
        except Exception as error:
            print("ResetPasswordSerializer_update_count_change_pass_error: ", error)
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
        ]  # 'username',
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"validators": [EmailValidator]},
        }

    def is_email_exist(self):
        try:
            user = User.objects.get(email=self.validated_data["email"])
            return True
        except:
            return False

    def save(self):
        user = User(
            email=self.validated_data["email"],
            username=self.validated_data["email"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
        )
        password = self.validated_data["password"]

        if len(password) < 5:
            raise serializers.ValidationError(
                {"password": "Password must be at least 5 characters."}
            )

        user.set_password(password)
        user.is_active = False
        user.save()
        try:
            profile = CareerProfile(user=user, phone=self.validated_data["phone"])
            profile.save()
            member_group = Group.objects.get(name=settings.GROUP_NAME["MEMBER"])
            member_group.user_set.add(user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            link_active = settings.FRONTEND_SITE_URL_ACTIVE_ACCOUNT + "".join(
                access_token
            )
            message = render_to_string(
                "api/mail/active_account.html",
                {"link_active": link_active, "email_title": settings.EMAIL_TITLE},
            )
            send = EmailMessage(
                settings.EMAIL_TITLE,
                message,
                from_email=settings.EMAIL_FROM,
                to=[self.validated_data["email"]],
            )
            send.content_subtype = "html"
            send.send()
            print("Sent email!")
        except:
            pass
        return user


class CareerCategoryLevel2Serializer(serializers.ModelSerializer):
    class Meta:
        model = CareerCategoryLevel2
        fields = [
            "id",
            "name",
            "description",
            "create_at",
            "update_at",
            "slug",
            "is_active",
            "career_category_level1_id",
        ]

    def validate(self, data):
        if not data.get("slug"):
            data["slug"] = slugify(unidecode(data["name"]))
        return data

    def is_name_exist(self):
        try:
            if CareerCategoryLevel2.objects.filter(
                name=self.validated_data.get("name"),
                career_category_level1_id=self.validated_data.get(
                    "career_category_level1_id"
                ),
            ).exists():
                return True
        except Exception as e:
            print(f"Error checking if name exists: {e}")
            return False

    def save(self):
        try:
            self.instance.name = self.validated_data.get("name", self.instance.name)
            self.instance.description = self.validated_data.get("description", self.instance.description)
            self.instance.slug = slugify(unidecode(self.validated_data.get("name", self.instance.name)))
            self.instance.career_category_level1_id = self.validated_data.get("career_category_level1_id", self.instance.career_category_level1_id)
            self.instance.save()
            return True
        except Exception as e:
            print(f"Error saving CareerCategoryLevel2: {e}")
            return None

    def add(self):
        try:

            # Tạo mới đối tượng CareerCategoryLevel1 với các giá trị đã được xác thực
            career_category_level_1 = CareerCategoryLevel2.objects.create(
                name=self.validated_data.get("name"),
                description=self.validated_data.get("description"),
                slug=slugify(unidecode(self.validated_data["name"])),
                career_category_level1_id=self.validated_data.get(
                    "career_category_level1_id"
                ),
            )
            return True
        except Exception as e:
            print(f"Error adding CareerCategoryLevel2: {e}")
            return None


class CareerCategoryLevel1Serializer(serializers.ModelSerializer):
    career_category_level_2 = CareerCategoryLevel2Serializer(
        many=True,
        read_only=True,
        source="career_category_level_1_w_career_category_level_2",
    )

    class Meta:
        model = CareerCategoryLevel1
        fields = [
            "id",
            "name",
            "description",
            "create_at",
            "update_at",
            "slug",
            "is_active",
            "icon",
            "career_category_level_2",
        ]

    def validate(self, data):
        if not data.get("slug"):
            data["slug"] = slugify(unidecode(data["name"]))
        return data

    def is_name_exist(self):
        try:
            if CareerCategoryLevel1.objects.filter(
                name=self.validated_data.get("name")
            ).exists():
                return True
        except Exception as e:
            print(f"Error checking if name exists: {e}")
            return False

    def save(self):
        try:
            self.instance.name = self.validated_data.get("name")
            self.instance.description = self.validated_data.get("description")
            self.instance.slug = slugify(unidecode(self.validated_data["name"]))
            self.instance.save()
            return True
        except Exception as e:
            print(f"Error saving CareerCategoryLevel1: {e}")
            return None

    def add(self):
        try:
            # Lấy đối tượng ImageLibrary từ validated_data
            icon = self.validated_data.get("icon")

            # Tạo mới đối tượng CareerCategoryLevel1 với các giá trị đã được xác thực
            CareerCategoryLevel1.objects.create(
                name=self.validated_data.get("name"),
                description=self.validated_data.get("description"),
                slug=slugify(unidecode(self.validated_data["name"])),
                is_active=self.validated_data.get("is_active", True),
                icon=icon,
            )
            return True
        except Exception as e:
            print(f"Error adding CareerCategoryLevel1: {e}")
            return None


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"


class RecruitmentPostSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(
        read_only=True,
        source='user_id'
    )

    class Meta:
        model = RecruitmentPost
        fields = [
            "title",
            "short_description",
            "job_description",
            "job_requirements",
            "benefits",
            "work_location_details",
            "created_at",
            "updated_at",
            "slug",
            "is_active",
            "views",
            "local_id",
            "oversea_id",
            'user_info',
            "user_id",
        ]

    def validate(self, data):
        if not data.get("slug"):
            data["slug"] = slugify(unidecode(data["title"]))
        return data

    def add(self):
        try:
            RecruitmentPost.objects.create(
                title=self.validated_data.get("title"),
                short_description=self.validated_data.get("short_description"),
                job_description=self.validated_data.get("job_description"),
                benefits=self.validated_data.get("benefits"),
                work_location_details=self.validated_data.get("work_location_details"),
                slug=slugify(unidecode(self.validated_data["title"])),
                local_id=self.validated_data.get("local_id"),
                oversea_id=self.validated_data.get("oversea_id"),
                user_id=self.validated_data.get("user_id"),
            )
            return True
        except Exception as e:
            print("CareerCategoryLevel2_RecruitmentPost adding errors: ", e)
            return False

    def save(self):
        try:
            self.instance.title = self.validated_data.get("title", self.instance.title)
            self.instance.short_description = self.validated_data.get("short_description", self.instance.short_description)
            self.instance.job_description = self.validated_data.get("job_description", self.instance.job_description)
            self.instance.benefits = self.validated_data.get("benefits", self.instance.benefits)
            self.instance.work_location_details = self.validated_data.get("work_location_details", self.instance.work_location_details)
            self.instance.slug = slugify(unidecode(self.validated_data.get("title", self.instance.title)))
            self.instance.local_id = self.validated_data.get("local_id", self.instance.local_id)
            self.instance.oversea_id = self.validated_data.get("oversea_id", self.instance.oversea_id)
            self.instance.user_id = self.validated_data.get("user_id", self.instance.user_id)
            self.instance.save()
            return True
        except Exception as e:
            print(f"Error saving RecruitmentPost: {e}")
            return None


class CareerCategoryLevel2_RecruitmentPost_Serializers(serializers.ModelSerializer):
    career_category_level2_id = CareerCategoryLevel2Serializer()
    recruitment_id = RecruitmentPostSerializer()

    class Meta:
        models = CareerCategoryLevel2_RecruitmentPost
        fields = ["career_category_level2_id", "recruitment_id"]

    def add(self):
        try:
            CareerCategoryLevel2_RecruitmentPost.objects.create(
                career_category_level2_id=self.validated_data.get(
                    "career_category_level2_id"
                ),
                recruitment_id=self.validated_data.get("recruitment_id"),
            )
            return True
        except Exception as e:
            print("CareerCategoryLevel2_RecruitmentPost adding errors: ", e)
            return False

    def save(self):
        try:
            self.instance.career_category_level2_id = self.validated_data.get(
                "career_category_level2_id", self.instance.career_category_level2_id
            )
            self.instance.recruitment_id = self.validated_data.get(
                "recruitment_id", self.instance.career_category_level2_id
            )
            self.instance.save()
            return True
        except Exception as e:
            print(f"Error saving CareerCategoryLevel2_RecruitmentPost: {e}")
            return None
