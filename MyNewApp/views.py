from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import *
from django.db.models import Q
from .models import *


headers = {"X-Api-Key": "36fedc81de23f05b7044ababd27d0555", "X-Auth-Token": "6fb6c5ad36a9baa8a7c734141a9535f3"}

""" Payment Gateway Integration
send_request > decide redirect url >  post request (Instamojo Server)  > 
    store unique Id > redirect on long url > ........... 
    > after redirect on url we will open unique Id  > 
    send get request with unique Id  (Instamojo Server) > accept the response > 
    check the status of payment.       

"""
import requests
import json
def SendPaymentRequest(request, u_id):
    Buyer = UserDataBase.objects.get(id = u_id)
    payload = {
        'purpose': 'Donate Amount to TechBlog',
        'amount': '10',
        'buyer_name': Buyer.name,
        'email': Buyer.email,
        'phone': Buyer.number,
        'redirect_url': 'http://127.0.0.1:8000/paycheck/',
        'send_email': 'True',
        'send_sms': 'True',
    }
    response = requests.post("https://www.instamojo.com/api/1.1/payment-requests/", data=payload, headers=headers)
    op = response.text
    data = json.loads(op)
    Pay_Id = data["payment_request"]["id"]
    d = PayId.objects.create(PaymentId = Pay_Id)
    longUrl = data["payment_request"]["longurl"]
    return redirect(longUrl)




def PaymentCheck(request):
    PaymentI = PayId.objects.all().order_by("-id")[0]
    PayI = PaymentI.PaymentId
    response = requests.get(
        "https://www.instamojo.com/api/1.1/payment-requests/{}/".format(PayI),
        headers=headers)
    op = response.text
    data = json.loads(op)
    status = data["payment_request"]["payments"][0]["status"]
    print(status)
    if status == "Failed":
        return HttpResponse("Try Again")
    else:
        return HttpResponse("You Paid..")



def SendSms(number, msg):
    import urllib
    import urllib.request as urllib2

    authkey = "232419AGxejpXap5eeb621aP1"
    mobiles = number
    sender = "lindin"
    msg = msg
    route = '4'

    Dict = {
        "authkey": authkey,
        "mobiles": mobiles,
        "message": msg,
        "sender": sender,
        "route": route
    }

    url = "http://api.msg91.com/api/sendhttp.php"
    postData = urllib.parse.urlencode(Dict)
    postData = postData.encode("ascii")
    req = urllib2.Request(url, postData)
    resp = urllib2.urlopen(req)
    op = resp.read()
    print("Send Msg:", msg)



from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
def SendEmail(email, msg):
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    html = get_template("mail.html").render({"msg":msg})
    #html = "<h1>Email</h1>"
    sub = "TechBlog - New Like"
    send_mail(sub, " ", from_email, to_email, html_message=html)



def Login(request):
    if request.user.is_authenticated():
        return redirect("UserProfile", request.user.username)

    form = AddUser_Form()
    error = False
    if request.method == "POST":
        un = request.POST["un"]
        ps = request.POST["ps"]
        usr = authenticate(username = un, password = ps)
        if usr != None:
            login(request, usr)
            return redirect("UserProfile", usr.username)
        error = True
    Dict = {
        "error":error, "form":form
    }
    return render(request, "login_register.html", Dict)



def Register(request):
    if request.method == "POST":
        form = AddUser_Form(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            un = request.POST["un"]
            ps = request.POST["ps"]
            email = data.email
            usr = User.objects.create_user(un, email, ps)
            data.usr = usr
            data.save()
            return redirect("login")
        error = True
    return HttpResponse("Register Your Self")


def Logout(request):
    logout(request)
    return redirect("login")



def UserProfile(request, Username):
    if not request.user.is_authenticated():
        return HttpResponse("Hello")
        return redirect("login")

    usr = User.objects.filter(username = Username)
    if not usr:
        return HttpResponse("Hello2")
        loggen_in_username = request.user.username
        return redirect("UserProfile", loggen_in_username)
    connection = None
    if request.user.username != Username:
        user1 = User.objects.get(username = Username)
        user2 = User.objects.get(username=request.user.username)
        UserData1 = UserDataBase.objects.get(usr = user1)
        UserData2 = UserDataBase.objects.get(usr = user2)
        connection = Connections.objects.filter(Q(sender=UserData1, receiver=UserData2) | Q(sender=UserData2, receiver=UserData1))
        if connection:
            connection = connection[0]


    Usr = usr[0]
    User_Detail = UserDataBase.objects.get(usr = Usr)
    blog_form = UserBlog_Form()

    all_posts = Blogs_Model.objects.filter(usr = Usr).order_by("-date")
    like_by_me_Ids = []
    all_likes_by_me = BlogLikes.objects.filter(usr = request.user)
    for i in all_likes_by_me:
        like_by_me_Ids.append(i.blog.id)

    Dict = {
        "Profile":User_Detail, "connection":connection,
        "form":blog_form, "all_posts":all_posts, "like_by_me_Ids":like_by_me_Ids
    }

    return render(request, "user_details.html", Dict)






def Update_User_Details(request, Username):
    if not request.user.is_authenticated():
        return redirect("login")

    loggen_in_username = request.user.username
    if Username != loggen_in_username:
        return redirect("UserProfile", loggen_in_username)

    usr = User.objects.filter(username=Username)
    Usr = usr[0]
    User_Detail = UserDataBase.objects.get(usr=Usr)

    form = Edit_User_Details(request.POST or None, request.FILES or None, instance=User_Detail)
    if form.is_valid():
        form.save()
        return redirect("UserProfile", loggen_in_username)

    Dict = {
        "Profile": User_Detail, "form":form
    }

    return render(request, "Update_User_Details.html", Dict)




def All_Profession(request, what):
    if not request.user.is_authenticated():
        return redirect("login")

    logged_in_user = User.objects.get(username = request.user.username)
    me = UserDataBase.objects.get(usr = logged_in_user)
    ###### Count Request Section #########
    con_request = Connections.objects.filter(receiver=me, status="Sent")
    con_sent = Connections.objects.filter(sender=me, status="Sent")
    con_friend = Connections.objects.filter(Q(sender=me, status="friend") | Q(receiver=me, status="friend")).order_by( "-date")

    #-----X Count Request Section End ---X_------#


    data = ""
    if what == "all":
        data = UserDataBase.objects.all()
    if what == "myreceived":
        connection = Connections.objects.filter(receiver=me, status = "Sent")
        User_Data = []
        for c in connection:
            ud = UserDataBase.objects.get(id = c.sender.id)
            User_Data.append(ud)
        data = User_Data
    if what == "Sent":
        connection = Connections.objects.filter(sender=me, status = "Sent")
        User_Data = []
        for c in connection:
            ud = UserDataBase.objects.get(id=c.receiver.id)
            User_Data.append(ud)
        data = User_Data
    if what == "Friends":
        connection = Connections.objects.filter(Q(sender=me, status = "friend") | Q(receiver=me, status = "friend")).order_by("-date")
        Data = []
        for c in connection:
            UserData = UserDataBase.objects.get(id = c.sender.id)
            if UserData.id != me.id:
                Data.append(UserData)

            UserData = UserDataBase.objects.get(id=c.receiver.id)
            if UserData.id != me.id:
                Data.append(UserData)
            data = Data
    Dict = {
        "all_users":data, "what":what, "con_request":con_request, "con_sent":con_sent,
        "con_friend":con_friend
    }
    return render(request, "professionals.html", Dict)



def All_Professional_Html(request, what):
    if not request.user.is_authenticated():
        return redirect("login")

    logged_in_user = User.objects.get(username = request.user.username)
    me = UserDataBase.objects.get(usr = logged_in_user)
    ###### Count Request Section #########
    con_request = Connections.objects.filter(receiver=me, status="Sent")
    con_sent = Connections.objects.filter(sender=me, status="Sent")
    con_friend = Connections.objects.filter(Q(sender=me, status="friend") | Q(receiver=me, status="friend")).order_by( "-date")

    #-----X Count Request Section End ---X_------#

    data = ""
    if what == "all":
        data = UserDataBase.objects.all()

    Dict = {
        "all_users": data, "what": what, "con_request": con_request, "con_sent": con_sent,
        "con_friend": con_friend, "me":me
    }

    return render(request, "professionals_html.html", Dict)





def Manage_your_connections(request, action, u_id):
    if not request.user.is_authenticated():
        return redirect("login")

    if action == "Send_Request":
        senderUser = User.objects.get(username = request.user.username)
        sender = UserDataBase.objects.get(usr = senderUser)
        receiver = UserDataBase.objects.get(id = u_id)
        Connections.objects.create(sender=sender, receiver=receiver)
        return redirect("UserProfile", receiver.usr.username)
    if action == "Accept_Request" or action == "Reject_Request":
        ReceiverUser = User.objects.get(username=request.user.username)
        receiver = UserDataBase.objects.get(usr=ReceiverUser)
        sender = UserDataBase.objects.get(id=u_id)
        connection = Connections.objects.filter(sender=sender, receiver=receiver)
        if connection:
            for c in connection:
                if action == "Accept_Request":
                    c.status = "friend"
                    c.save()
                if action == "Reject_Request":
                    c.status = "rejected"
                    c.save()

        return redirect("professional", "all")

    return HttpResponse("You want " + str(action) + "For User " + str(u_id))


def Add_Company(request):

    if not request.user.is_authenticated():
        return redirect("login")
    form = StartCompany_Form()
    if request.method == "POST":
        form = StartCompany_Form(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            Map = data.map_embad
            if 'width="600"' in Map:
                Map = Map.split('width="600"')
                Map.insert(1, 'width="100%"')
                Map = " ".join(Map)
                data.map_embad = Map
            data.usr = request.user
            data.save()
            return redirect("login")

    Dict = {
        "form":form
    }
    return render(request, "add_company.html", Dict)


def CompanyDetails(request):
    if not request.user.is_authenticated():
        return redirect("login")

    usr = request.user
    company = Company_Model.objects.filter(usr = usr)
    print(company)
    if not company:
        return redirect("login")

    Dict = {
        "company":company
    }
    return render(request, "companies_detail.html",Dict)




def NewPost(request):
    if request.method == "POST":
        form = UserBlog_Form(request.POST)
        if form.is_valid():
            data = form.save(commit = False)
            data.usr = request.user
            data.save()
            print("Blog Submitted...@")
    return redirect("login")


def Like_By_Me(request, b_id, Username):
    if not request.user.is_authenticated():
        return redirect("login")


    msg = "Hi, "
    blog = Blogs_Model.objects.get(id = b_id)

    #BlogLikes.objects.create(usr=request.user, blog=blog)
    user = User.objects.get(username = blog.usr.username)
    Ud = UserDataBase.objects.get(usr = user)
    name = Ud.name.split()[0]
    number = Ud.number
    email = Ud.email
    n_likes = len(BlogLikes.objects.filter(blog=blog))
    msg = "Hi, {name}! You got new Like for blog - *{title}*. And total likes for this Blog is {likes}.".format(name = name,title = blog.title, likes = n_likes )
    #SendSms(number, msg)
    SendEmail(email, msg)

    return redirect("UserProfile", Username)
