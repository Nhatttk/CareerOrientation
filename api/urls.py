
from django.conf.urls import include
from django.urls import path

from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from .serializers import MyTokenObtainPairView
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

history_log_get_all_api = HistoryLogMVS.as_view(
    {'get': 'history_log_get_all_api'})
# upload_avatar_user_api = UploadAvatarUserMVS.as_view(
#     {'patch': 'upload_avatar_user_api'})
profile_check_exist_api = ProfileMVS.as_view(
    {'post': 'profile_check_exist_api'})
profile_add_api = ProfileMVS.as_view({'post': 'profile_add_api'})

upload_avatar_career_profile_api = UploadAvatarCareerProfile.as_view(
    {'patch': 'upload_avatar_career_profile_api'})

check_and_create = UserCareerProfileViewSet.as_view(
    {'post': 'check_and_create'})

get_all_user_profile = UserCareerProfileViewSet.as_view(
    {'get': 'get_all_user_profile'})

# router = DefaultRouter()
# router.register(r'profiles', CareerProfileViewSet)
# router.register(r'image-library-categories', ImageLibraryCategoryViewSet)
# router.register(r'image-libraries', ImageLibraryViewSet)
# router.register(r'categories-level-1', CareerCategoryLevel1ViewSet)
# router.register(r'categories-level-2', CareerCategoryLevel2ViewSet)

# danh muc level 1
career_category_level_1_get_all_api = CareerCategoryLevel1MVS.as_view({'get': 'career_category_get_all_api'})
career_category_level_1_get_by_id_api = CareerCategoryLevel1MVS.as_view({'get': 'career_category_get_by_id_api'})
career_category_level_1_create_api = CareerCategoryLevel1MVS.as_view({'post': 'career_category_create_api'})
career_category_level_1_update_api = CareerCategoryLevel1MVS.as_view({'put': 'career_category_update_api'})
career_category_level_1_partial_update_api = CareerCategoryLevel1MVS.as_view({'patch': 'career_category_partial_update_api'})
career_category_level_1_delete_api = CareerCategoryLevel1MVS.as_view({'delete': 'career_category_delete_api'})


# danh muc level 2
career_category_level_2_get_all_api = CareerCategoryLevel2MVS.as_view({'get': 'career_category_get_all_api'})
career_category_level_2_get_by_id_api = CareerCategoryLevel2MVS.as_view({'get': 'career_category_get_by_id_api'})
career_category_level_2_create_api = CareerCategoryLevel2MVS.as_view({'post': 'career_category_create_api'})
career_category_level_2_update_api = CareerCategoryLevel2MVS.as_view({'put': 'career_category_update_api'})
career_category_level_2_partial_update_api = CareerCategoryLevel2MVS.as_view({'patch': 'career_category_partial_update_api'})
career_category_level_2_delete_api = CareerCategoryLevel2MVS.as_view({'delete': 'career_category_delete_api'})


# bai viet tuyen dung
recruitment_post_get_all_api = RecruitmentPostMVS.as_view({'get': 'recruitment_post_get_all_api'})
recruitment_post_get_by_id_api = RecruitmentPostMVS.as_view({'get': 'recruitment_post_get_by_id_api'})
recruitment_post_create_api = RecruitmentPostMVS.as_view({'post': 'recruitment_post_create_api'})
recruitment_post_update_api = RecruitmentPostMVS.as_view({'put': 'recruitment_post_update_api'})
recruitment_post_partial_update_api = RecruitmentPostMVS.as_view({'patch': 'recruitment_post_partial_update_api'})
recruitment_post_delete_api = RecruitmentPostMVS.as_view({'delete': 'recruitment_post_delete_api'})

urlpatterns = [
    # user
    path('account/get-user-profile/', get_profile_view),
    path('account/update-user-profile/', update_user_profile_view),
    path('account/update-user/', update_user_view),
    path('account/change-password/', change_password_view),
    path('account/history-log-get-all/', history_log_get_all_api),
    # path('account/upload-avatar-user/', upload_avatar_user_api),
    path('account/profile-check-exist/', profile_check_exist_api),
    path('account/profile-add/', profile_add_api),
    path('account/user/check-and-create/', check_and_create),

    
    # auth
    path('auth/google/', GoogleView.as_view(), name='google'),
    path('auth/login/', MyTokenObtainPairView.as_view()),
    # #
    path('system/', include('api.system.urls')),

    # get token 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # career-profile
    # path('career/', include(router.urls)),
    path('career/upload_avatar_career_profile_api/', upload_avatar_career_profile_api),
    path('career/get_all_user_profile/', get_all_user_profile),

    # category level 1
    path('career-category-level-1-get-all/', career_category_level_1_get_all_api),
    path('career-category-level-1-get-by-id/', career_category_level_1_get_by_id_api),
    path('career-category-level-1-create/', career_category_level_1_create_api),
    path('career-category-level-1-update/', career_category_level_1_update_api),
    path('career-category-level-1-partial-update/', career_category_level_1_partial_update_api),
    path('career-category-level-1-delete/', career_category_level_1_delete_api),

    # category level 2
    path('career-category-level-2-get-all/', career_category_level_2_get_all_api),
    path('career-category-level-2-get-by-id/', career_category_level_2_get_by_id_api),
    path('career-category-level-2-create/', career_category_level_2_create_api),
    path('career-category-level-2-update/', career_category_level_2_update_api),
    path('career-category-level-2-partial-update/', career_category_level_2_partial_update_api),
    path('career-category-level-2-delete/', career_category_level_2_delete_api),
    
    # RecruitmentPostMVS
    path('recruitment-post-get-all/', recruitment_post_get_all_api),
    path('recruitment-post-get-by-id/', recruitment_post_get_by_id_api),
    path('recruitment-post-create/', recruitment_post_create_api),
    path('recruitment-post-update/', recruitment_post_update_api),
    path('recruitment-post-partial-update/', recruitment_post_partial_update_api),
    path('recruitment-post-delete/', recruitment_post_delete_api),
]
