
from django.conf.urls import url
from django.contrib import admin
from MyNewApp.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', Login, name="login"),
    url(r'^Register/$', Register, name="register"),
    url(r'^logout/$', Logout, name="logout"),
    url(r'^india/(?P<Username>[\w-]+)/$', UserProfile, name="UserProfile"),

    url(r'^in/Edit/(?P<Username>[\w-]+)/$', Update_User_Details, name="UpdateUserProfile"),

    url(r'^all_professionals/(?P<what>[\w-]+)/$', All_Profession, name="professional"),
    url(r'^professional_html/(?P<what>[\w-]+)/$', All_Professional_Html, name="professional_html"),
    url(r'^connection/(?P<action>[\w-]+)/(?P<u_id>[0-9]+)/$', Manage_your_connections, name="connections"),

    url(r'^add_company/$', Add_Company, name="addCompany"),
    url(r'^your_company_details/$', CompanyDetails, name="CompanyDetails"),
    url(r'^post_new_blog/$', NewPost, name="post"),
    url(r'^likes/(?P<b_id>[\w-]+)/(?P<Username>[\w-]+)/$', Like_By_Me, name="likes"),

    url(r'^donate_amount/(?P<u_id>[\w-]+)/$', SendPaymentRequest, name="donate"),
    url(r'^paycheck/$', PaymentCheck, name="paycheck"),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
