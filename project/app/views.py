from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from .models import *
import requests, random
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from docx import Document
from django.contrib import messages

# Create your views here.
def index(request):   
    username=None
    navbar='index'
    courses = Course.objects.all()

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')

    context = {
        'navbar': navbar,
        'courses': courses,
        'username': username
    }
    return render(request, 'v2/index.html',context)


def login(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            context = {'error': "Parollar bir-biriga mos emas!"}
            return render(request, 'register.html', context)

        # Username va email unikalligini tekshirish
        if User.objects.filter(login=username).exists():
            context = {'error': "Bu foydalanuvchi nomi allaqachon mavjud."}
            return render(request, 'register.html', context)


        # Yangi foydalanuvchini yaratish
        rolename=Role.objects.filter(name='Talaba').first()
        hashed_password = make_password(password)
        User.objects.create(
            fullname=fullname,
            login=username,
            password=hashed_password,
            role=rolename
        )
        context = {'success': "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi! Endi tizimga kiring."}
        # return render(request, 'register.html', context)
    return render(request, 'register.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Foydalanuvchini autentifikatsiya qilish
        user = User.objects.filter(login=username).first()
        if user and check_password(password, user.password) and user.role.name == 'Talaba':
            # Tizimga kirish (login qilish)
            request.session['user_id']=user.pk
            request.session['username']=user.login
            return redirect('index')  # Tizimga kirgandan keyin boshqa sahifaga yo'naltirish
        elif user and check_password(password, user.password) and user.role.name == 'Adminstrator':
            request.session['user_id']=user.pk
            request.session['username']=user.login
            return redirect('index')
        else:
            return redirect('login') 

    return render(request, 'register.html')

def courses(request): 
    navbar='courses'  
    username=None
    courses = Course.objects.all()

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    # if userID is not None and userRole is not None:
    if True:
        username=request.session.get('username')
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'courses': courses,
        'username': username
    }
    return render(request, 'v2/courses.html',context)

def course(request, pk): 
    navbar='courses'  
    username=None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        with connection.cursor() as cursor:
            cursor.execute(f""" 
                select
                    *
                from app_course cr
            """)
            courses=cursor.fetchall()
            cursor.execute(""" 
                select
                    th.id,
                    th.name
                from app_thema th
                where th.course_id= %s
            """, (int(pk), ))
            thema = cursor.fetchall()
            cursor.execute(""" 
                SELECT 
                    mr.id, 
                    mr.name, 
                    CASE 
                        WHEN lg.user_id IS NULL THEN 'O`qilmagan' 
                        ELSE 'O`qilgan' 
                    END AS uqish,
                    th.id
                FROM app_maruza mr
                inner join app_thema th on mr.thema_id = th.id
                LEFT JOIN app_maruzalog lg 
                    ON mr.id = lg.maruza_id AND lg.user_id = %s
                where th.course_id=%s
            """, (int(userID), int(pk), ))
            maruza = cursor.fetchall()
            cursor.execute(""" 
                SELECT 
                    mr.id, 
                    mr.name, 
                    CASE 
                        WHEN lg.user_id IS NULL THEN 'O`qilmagan' 
                        ELSE 'O`qilgan' 
                    END AS uqish,
                    th.id
                FROM app_video mr
                inner join app_thema th on mr.thema_id = th.id
                LEFT JOIN app_videolog lg 
                    ON mr.id = lg.video_id AND lg.user_id = %s
                where th.course_id=%s
            """, (int(userID), int(pk), ))
            video = cursor.fetchall()
            cursor.execute(""" 
                select
                mr.id,
                mr.name,
                case when lg.user_id is null then 'O`qilmagan'
                else 'O`qilgan' end uqish,
                th.id
            from app_taqdimot mr
            inner join app_thema th on mr.thema_id = th.id
            left join app_taqdimotlog lg on mr.id = lg.taqdimot_id and  lg.user_id= %s
            where th.course_id= %s
                        """, (int(userID), int(pk), ))
            taqdimot = cursor.fetchall()
            cursor.execute(""" 
                select
                    tn.id,
                    tn.name,
                    th.id,
                    case when l.status = true then 'Bajarilgan' else 'Bajarilmagan' end status
                from app_testname tn
                inner join app_thema th on tn.thema_id = th.id
                left join app_testlog l on tn.id = l.test_id and l.user_id=%s
                where th.course_id= %s
                        """, (int(userID) ,int(pk),))
            testthema = cursor.fetchall()
            # sertifikat olish imkoniyatini tekshirish
            cursor.execute(f""" 
                with maruza as (select count(m.id) as qoldi
                            from app_maruza m
                                    left join main.app_maruzalog am on m.id = am.maruza_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                            where at.course_id = {int(pk)}
                            and am.id is null),
                taqdimot as (select count(m.id) as qoldi
                            from app_taqdimot m
                                    left join main.app_taqdimotlog am on m.id = am.taqdimot_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                            where at.course_id = {int(pk)}
                                and am.id is null),
                video as (select count(m.id) as qoldi
                        from app_video m
                                    left join main.app_videolog am on m.id = am.video_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                        where at.course_id = {int(pk)}
                            and am.id is null),
                test as (select count(m.id) as qoldi
                        from app_testname m
                                left join main.app_testlog am on m.id = am.test_id and am.user_id = {int(userID)}
                                inner join main.app_thema at on m.thema_id = at.id
                        where at.course_id = {int(pk)}
                            and am.id is null)
            select case when m.qoldi == 0 and t.qoldi == 0 and v.qoldi == 0 and ts.qoldi == 0 then true else false end status
            from maruza m,
                taqdimot t,
                video v,
                test ts
            """)
            cerf_status=cursor.fetchone()


    else:
        return redirect('index')

    context = {
        'navbar': navbar,
        'maruza': maruza,
        'taqdimot': taqdimot,
        'testthema': testthema,
        'thema': thema,
        'courses': courses,
        'username': username,
        'userID': userID,
        'pk': pk,
        'video': video,
        'cerf_status': cerf_status
    }
    return render(request, 'v2/course.html',context)

def maruza(request, pk): 
    navbar='courses'  
    username=None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        maruza=Maruza.objects.filter(id=int(pk)).first()
        MaruzaLog.objects.get_or_create(
            user=userRole,
            maruza=maruza,
            status=True
        )
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'maruza': maruza,
        'username': username
    }
    return render(request, 'v2/view_maruza.html',context)

def video(request, pk): 
    navbar='courses'  
    username=None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        video=Video.objects.filter(id=int(pk)).first()
        VideoLog.objects.get_or_create(
            user=userRole,
            video=video,
            status=True
        )
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'video': video,
        'username': username
    }
    return render(request, 'v2/view_video.html',context)

def taqdimot(request, pk): 
    navbar='courses'  
    username=None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        maruza=Taqdimot.objects.filter(id=int(pk)).first()
        TaqdimotLog.objects.get_or_create(
            user=userRole,
            taqdimot=maruza,
            status=True
        )
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'maruza': maruza,
        'username': username
    }
    return render(request, 'v2/view_present.html',context)

def logout(request):
    request.session.flush()  # Barcha sessiya ma’lumotlarini o'chiradi
    return redirect('index')

def test(request, pk): 
    navbar='courses'  
    username=None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    AllTests = []
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        with connection.cursor() as cursor:
            app_testrunID=int(pk)
            cursor.execute(""" 
                select
                    ts.id,
                    ts.name,
                    ts.key1,
                    ts.key2,
                    ts.key3,
                    ts.key4
                from app_test ts
                where ts.test_name_id= %s
                ORDER BY RANDOM()
                LIMIT 10;
            """, (int(pk), ))
            tests = cursor.fetchall()
            AllTests.append(tests)
            for test_group in AllTests:
                for test in test_group:
                    question_id, question_text, *options = test  # Savol va variantlarni ajratish
                    random.shuffle(options)  # Variantlarni aralashtirish
                    test_group[test_group.index(test)] = (question_id, question_text, *options)  # Yangi tartibni qayta yozish
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'AllTests': AllTests,
        'app_testrunID': app_testrunID,
        'username': username
    }
    return render(request, 'view_test.html',context)

def scan_test(request, pk=None): 
    navbar='courses'  
    username=None
    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()
    if userID is not None and userRole is not None:
        username=request.session.get('username')
        if request.method == 'POST':
            counter = 0
            testrun = request.POST.get('testrun')
            testrun=TestName.objects.filter(pk=int(testrun)).first()
            results = {}
            for key, value in request.POST.items():
                if key.startswith('q'):
                        results[key] = value

                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT ts.id FROM main.app_test ts WHERE ts.id=%s AND ts.key1=%s",
                                [int(key[1:]), value]  # key[1:] bilan 'q' ni olib tashlaymiz
                            )
                            scan=cursor.fetchone()
                            if scan is None:
                                counter+=0
                            else:
                                counter+=1
                        if counter >= 8:
                            TestLog.objects.update_or_create(
                                user=userRole,
                                test=testrun,
                                defaults={ 'status': True }
                            )
                        else:
                            TestLog.objects.update_or_create(
                                user=userRole,
                                test=testrun,
                                defaults={ 'status': False }
                            )
                            
    else:
        return redirect('index')
    context = {
        'navbar': navbar,
        'username': username,
        'counter': counter,
        'userRole': userRole
    }
    return render(request, 'view_result.html',context)

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.db import connection
from docx import Document
from .models import User, Role, Course  # Model import qilamiz

def certificate(request, user, pk): 
    navbar = 'courses'
    username = None

    userID = request.session.get('user_id')
    roleName = Role.objects.filter(name='Talaba').first()
    userRole = User.objects.filter(pk=userID, role=roleName).first()

    if userID is not None and userRole is not None:
        username = request.session.get('username')

        with connection.cursor() as cursor:
            # Ma'ruza tekshirish
            cursor.execute("""
                SELECT mr.id FROM app_maruzalog lg
                RIGHT JOIN app_maruza mr ON lg.maruza_id = mr.id
                INNER JOIN app_thema th ON mr.thema_id = th.id
                WHERE th.course_id=%s AND lg.user_id=%s AND lg.status=false
            """, (int(pk), int(user)))
            maruza = cursor.fetchall()

            # Taqdimot tekshirish
            cursor.execute("""
                SELECT mr.id FROM app_taqdimotlog lg
                RIGHT JOIN app_taqdimot mr ON lg.taqdimot_id = mr.id
                INNER JOIN app_thema th ON mr.thema_id = th.id
                WHERE th.course_id=%s AND lg.user_id=%s AND lg.status=false
            """, (int(pk), int(user)))
            taqdimot = cursor.fetchall()

            # Test tekshirish
            cursor.execute("""
                SELECT n.name FROM app_testlog lg
                RIGHT JOIN app_testname n ON lg.test_id = n.id
                INNER JOIN main.app_thema at ON n.thema_id = at.id
                WHERE at.course_id=%s AND lg.user_id=%s AND lg.status=false
            """, (int(pk), int(user)))
            test = cursor.fetchall()
            cursor.execute(f""" 
                with maruza as (select count(m.id) as qoldi
                            from app_maruza m
                                    left join main.app_maruzalog am on m.id = am.maruza_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                            where at.course_id = {int(pk)}
                            and am.id is null),
                taqdimot as (select count(m.id) as qoldi
                            from app_taqdimot m
                                    left join main.app_taqdimotlog am on m.id = am.taqdimot_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                            where at.course_id = {int(pk)}
                                and am.id is null),
                video as (select count(m.id) as qoldi
                        from app_video m
                                    left join main.app_videolog am on m.id = am.video_id and am.user_id = {int(userID)}
                                    inner join main.app_thema at on m.thema_id = at.id
                        where at.course_id = {int(pk)}
                            and am.id is null),
                test as (select count(m.id) as qoldi
                        from app_testname m
                                left join main.app_testlog am on m.id = am.test_id and am.user_id = {int(userID)}
                                inner join main.app_thema at on m.thema_id = at.id
                        where at.course_id = {int(pk)}
                            and am.id is null)
            select case when m.qoldi == 0 and t.qoldi == 0 and v.qoldi == 0 and ts.qoldi == 0 then true else false end status
            from maruza m,
                taqdimot t,
                video v,
                test ts
            """)
            cerf_status=cursor.fetchone()

        # **Shartni to‘g‘ri tekshirish** (Agar *birorta* shart bajarilmagan bo‘lsa)
        if cerf_status[0] == False:
            messages.error(request, "Siz sertifikat olish shartlarini bajarmadingiz!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # Foydalanuvchini sertifikat sahifasiga qaytarish

        # **Foydalanuvchi va kurs nomini dinamik olish**
        user_obj = User.objects.get(pk=user)
        course_obj = Course.objects.get(pk=pk)

        template_path = "media/certificate_template.docx"  # Faylni media papkada saqlash
        doc = Document(template_path)

        replacements = {
            "{fullname}": user_obj.fullname,  # Foydalanuvchi ismini qo'shamiz
            "{course}": course_obj.name,       # Kurs nomini qo'shamiz
        }

        for paragraph in doc.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response["Content-Disposition"] = f'attachment; filename="certificate.docx"'
        doc.save(response)
        return response

    else:
        return redirect('index')
