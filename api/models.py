from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

# from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField

from api.submodels.models_media import *

# Account ================================================================================

# # https://www.youtube.com/watch?v=Sc1KKe1Pguw
# def profile_upload_path(instance, filename):
#     return '/'.join(['folder', str(instance.phone), filename])

# PNG_TYPE_IMAGE = "PNG_TYPE_IMAGE"
# JPG_TYPE_IMAGE = "JPG_TYPE_IMAGE"
# JPEG_TYPE_IMAGE = "JPEG_TYPE_IMAGE"
# GIF_TYPE_IMAGE = "GIF_TYPE_IMAGE"
# MP4_TYPE_VIDEO = "MP4_TYPE_VIDEO"
# IMAGE_TYPE_CHOICES = [
#     (PNG_TYPE_IMAGE, 'PNG image type'),
#     (JPG_TYPE_IMAGE, 'JPG image type'),
#     (JPEG_TYPE_IMAGE, 'JPEG image type'),
#     (GIF_TYPE_IMAGE, 'GIP image type')
# ]
# VIDEO_TYPE_CHOICES = [
#     (MP4_TYPE_VIDEO, 'MP4 video type'),
# ]


class Profile(models.Model):
    user = models.OneToOneField(
        User, related_name='user_w_profile', on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    gender = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, null=True)
    facebook = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to='images/avatars/',
                               default='images/avatars/avatar_default.png', null=True, blank=True)
    is_mentor = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)
    is_algorithm_mentor = models.BooleanField(default=False)
    count_change_password = models.IntegerField(default=0)
    is_sub_mentor = models.BooleanField(default=False)

    class Meta:
        ordering = ('user',)

    def __str__(self):
        return self.user.email + "(Edu Mentor: " + str(self.is_mentor) + ", Leader Support: " + str(self.is_sub_mentor) + ", Algorithm Mentor: " + str(self.is_algorithm_mentor) + ")"
        # if self.is_algorithm_mentor:
        #     return self.user.email + "(Algorithm Mentor)"
        # if self.is_school_admin:
        #     return self.user.email + "(School Admin)"
        # if self.is_mentor:
        #     return self.user.email + "(Edu Mentor)"


class SessionToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=500, null=True, blank=False)
    hostname = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    mac_address = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class HistoryLog(models.Model):
    user = models.ForeignKey(User, related_name='user_w_history_log',
                             on_delete=models.SET_NULL, blank=False, null=True)
    hostname = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    mac_address = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=100, null=True, blank=True)

# ==============================================================================


class Setting(models.Model):
    is_lock_login = models.BooleanField(default=False)

    def __str__(self):
        return "Lock Login: " + str(self.is_lock_login)


class CareerProfile(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    gender = models.BooleanField(default=True)
    phone = models.CharField(max_length=255,blank=True, null=True)
    avatar = models.ForeignKey(ImageLibrary,related_name='image_library_w_career_profile', on_delete=models.SET_NULL, blank=False, null=True)
    youtube = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)  
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_teacher_mentor = models.BooleanField(default=False)
    is_college_student = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_support_staff = models.BooleanField(default=False)
    count_change_password = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, related_name='user_w_career_profile',
                             on_delete=models.SET_NULL, blank=False, null=True)

class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    number_of_employees = models.CharField(max_length=255) # quy mô nhân viên (ex : 24 - 100, ...)
    description = RichTextField(blank=True, null=True) 
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)    
    user_id = models.ForeignKey(User, related_name="user_w_company_profile", on_delete=models.CASCADE, blank=False, null=True)


class CareerCategoryLevel1(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True) 
    icon = models.ForeignKey(ImageLibrary,related_name='image_library_w_career_category_level_1', on_delete=models.SET_NULL, blank=False, null=True)


class CareerCategoryLevel2(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True) 
    career_category_level1_id = models.ForeignKey(CareerCategoryLevel1,related_name='career_category_level_1_w_career_category_level_2', on_delete=models.SET_NULL, blank=False, null=True)

class Region(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LocalAreas(models.Model):
    city = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region_id = models.ForeignKey(Region, related_name="region_w_local_areas", on_delete=models.SET_NULL, blank=True, null=True)

class OverseasAreas(models.Model):
    oversea_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    region_id = models.ForeignKey(Region, related_name="region_w_overseas_areas", on_delete=models.SET_NULL, blank=True, null=True)

class RecruitmentPost(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    job_description = models.TextField()
    job_requirements = models.TextField()
    benefits = models.TextField()
    work_location_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    local_id = models.ForeignKey(LocalAreas, related_name="local_areas_w_recruitment_post", on_delete=models.SET_NULL, blank=True, null=True)
    oversea_id = models.ForeignKey(OverseasAreas, related_name="overseas_areas_w_recruitment_post", on_delete=models.SET_NULL, blank=True, null=True)
    user_id = models.ForeignKey(User, related_name='user_w_recruitment_post',
                             on_delete=models.SET_NULL, blank=True, null=True)

class ApplicationProfile(models.Model):
    cv = models.ForeignKey(DocumentLibrary, related_name="document_library_w_application_profile", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, related_name='user_w_application_profile',
                             on_delete=models.CASCADE, blank=False, null=True)  # Ideally should be a ForeignKey to a User model
    recruitment_id = models.ForeignKey(RecruitmentPost, related_name='recruitment_post_w_application_profile',
                             on_delete=models.CASCADE, blank=False, null=True)

class CareerCategoryLevel2_RecruitmentPost(models.Model):
    career_category_level2_id = models.ForeignKey(CareerCategoryLevel2, 
                            related_name="career_category_level2_w_career_category_level2_recruitment_post",
                            on_delete=models.CASCADE, blank=True, null=True)
    recruitment_id = models.ForeignKey(RecruitmentPost, 
                            related_name="recruitment_post_w_career_category_level2_recruitment_post",
                            on_delete=models.CASCADE, blank=True, null=True)

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    content = RichTextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    title_img = models.ForeignKey(ImageLibrary,related_name='image_library_w_blog_post', on_delete=models.SET_NULL, blank=False, null=True)
    views = models.IntegerField(default=0)
    time_take_place = models.DateTimeField()
    local_id = models.ForeignKey(LocalAreas, related_name="local_areas_w_blog_post", on_delete=models.SET_NULL, blank=True, null=True)
    oversea_id = models.ForeignKey(OverseasAreas, related_name="overseas_areas_w_blog_post", on_delete=models.SET_NULL, blank=True, null=True)


class CareerCategory2_BlogPost(models.Model):
    career_category_level2_id = models.ForeignKey(CareerCategoryLevel2, 
        related_name="career_category_level2_w_career_category_level_2_blog_post", on_delete=models.CASCADE)
    blog_id = models.ForeignKey(BlogPost, 
        related_name="blog_post_w_career_category_level_2_blog_post",on_delete=models.CASCADE)

class SchoolPost(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=255)
    tuition = models.CharField(max_length=255)
    graduation_exam_score = models.CharField(max_length=255)
    number_of_student = models.IntegerField()
    infrastructure = models.CharField(max_length=255)
    employment_rate_after_graduation = models.CharField(max_length=255)
    instructor_educational_background = models.CharField(max_length=255)
    local_id = models.ForeignKey(LocalAreas, related_name="local_areas_w_school_post", on_delete=models.SET_NULL, blank=True, null=True)
    logo = models.ForeignKey(ImageLibrary,related_name='image_library_w_school_post', on_delete=models.SET_NULL, blank=False, null=True)
    career_category_level2_id = models.ForeignKey(CareerCategoryLevel2, 
        related_name="career_category_level2_w_school_post", on_delete=models.CASCADE)

class QAPost(models.Model):
    content = RichTextField()
    create_at = models.DateTimeField(auto_now_add=True)  
    update_at = models.DateTimeField(auto_now=True)  
    slug = models.SlugField(max_length=255, unique=True)  
    is_active = models.BooleanField(default=True)  
    like = models.IntegerField(default=0)  
    views = models.IntegerField(default=0)  
    user_id = models.ForeignKey(User, related_name='user_w_qa_post',
                             on_delete=models.CASCADE, blank=False, null=True)

class CareerCategory2_QAPost(models.Model):
    career_category_level2 = models.ForeignKey(CareerCategoryLevel2, 
            related_name="career_category_level2_w_career_category_level_2_qa_post", on_delete=models.CASCADE)
    qa_post = models.ForeignKey(QAPost, 
            related_name="qa_post_w_career_category_level_2_blog_post", on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField() 
    create_at = models.DateTimeField(auto_now_add=True)  
    update_at = models.DateTimeField(auto_now=True) 
    is_active = models.BooleanField(default=True) 
    like = models.IntegerField(default=0)  
    user_id = models.ForeignKey(User, related_name='user_w_comment',
                             on_delete=models.CASCADE, blank=False, null=True)
    qa_post = models.ForeignKey(User, related_name='qa_post_w_comment',
                             on_delete=models.CASCADE, blank=False, null=True)

class Reply(models.Model):
    content = models.TextField()  
    create_at = models.DateTimeField(auto_now_add=True)  
    update_at = models.DateTimeField(auto_now=True)  
    is_active = models.BooleanField(default=True) 
    like = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, related_name='user_w_reply',
                             on_delete=models.CASCADE, blank=False, null=True)
    comment_id = models.ForeignKey(User, related_name='comment_w_reply',
                             on_delete=models.CASCADE, blank=False, null=True)


class QAPost_Follower(models.Model):
    qa_post = models.ForeignKey(QAPost,related_name="qa_post_w_qa_post_follower" ,on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_w_qa_post_follower",on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True) 

class QAPost_Notifications(models.Model):
    message = models.CharField(max_length=255)
    create_at = models.DateTimeField()  
    qa_post = models.ForeignKey(QAPost,related_name="qa_post_w_qa_post_notifications", on_delete=models.CASCADE)  
    user = models.ForeignKey(User,related_name="user_w_qa_post_notifications", on_delete=models.CASCADE) 
