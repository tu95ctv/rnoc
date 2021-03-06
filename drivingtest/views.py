# -*- coding: utf-8 -*-
#from django.db.models import F
from drivingtest.models import SpecificProblem, FaultLibrary, EditHistory
from django.db.models.fields.related import ForeignKey, ManyToManyField
import os
from django.template import RequestContext
from django.shortcuts import render_to_response, render
import models
from models import Table3g, Ulnew,\
    ForumTable, PostLog, LeechSite, thongbao, postdict, Mll, Command3g,SearchHistory, H_Field, Doitac, Nguyennhan,TrangThaiCuaTram, Duan
    
from drivingtest.forms import  UploadFileForm, Table3gForm, ForumChoiceForm, UlnewForm ,\
    Table3gTable, MllForm, MllTable, Command3gTable, Command3gForm, SearchHistoryTable,\
    CommentForMLLForm,  NTP_Field,ModelManagerForm, UserProfileForm_re
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from load_driving_tests import read_txt, insert_to_db
from __main__ import sys
from fetch_website import danhsachforum, PostObject, leech_bai,\
    get_link_from_db, init_d4, import_ul_txt_to_myul
from drivingtest.forms import PersonTable
import operator
from django.conf import settings #or from my_project import settings
from itertools import chain
from toold4 import  recognize_fieldname_of_query
from LearnDriving.settings import MYD4_LOOKED_FIELD, FORMAT_TIME
from xu_ly_db_3g import tao_script_r6000_w12, import_database_4_cai_new
import xlrd
import re
from exceptions import Exception
import ntpath
from sendmail import send_email
from django_tables2_reports.config import RequestConfigReport as RequestConfig


from django.db.models import CharField,DateTimeField
from django.utils import  simplejson
from drivingtest.forms import UserForm, UserProfileForm
import forms#cai nay quan trong khong duoc xoa


################CHUNG######################
def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm_re(data=request.POST)

        # If the two forms are valid...
        user_form.is_valid() 
        print '@@#$#',user_form.cleaned_data['email']
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
    
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
    
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
    
            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            '''
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            '''
    
            # Now we save the UserProfile model instance.
            profile.save()
    
            # Update our variable to tell the template registration was successful.
            registered = True
    
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'drivingtest/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    print request
    
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/omckv2/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('drivingtest/login.html', {}, context) 
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/omckv2/')





#####OMC###############



@login_required
def omckv2(request):
    #print 'request',request
    #mllform = MllForm(instance = Mll.objects.latest('id'))
    table3gform = Table3gForm()
    mllform = MllForm()
    commandform = Command3gForm()
    mlltable = MllTable(Mll.objects.all().order_by('-id'))
    RequestConfig(request, paginate={"per_page": 15}).configure(mlltable) 
    lenhtable = Command3gTable(Command3g.objects.all().order_by('-id'))
    RequestConfig(request, paginate={"per_page": 15}).configure(lenhtable) 
    #table = Table3gTable(Table3g.objects.all(), )
    table3gtable = Table3gTable(Table3g.objects.all(), )
    RequestConfig(request, paginate={"per_page": 10}).configure(table3gtable)
    history_search_table = SearchHistoryTable(SearchHistory.objects.all().order_by('-search_datetime'), )
    RequestConfig(request, paginate={"per_page": 10}).configure(history_search_table)
    comment_form = CommentForMLLForm()
    model_manager_form = ModelManagerForm()
    #comment_form.fields['datetime'].widget = forms.HiddenInput()
    return render(request, 'drivingtest/omckv2.html',{'table3gtable':table3gtable,'table3gform':table3gform,'mllform':mllform,'comment_form':comment_form,\
            'commandform':commandform,'mlltable':mlltable,'lenhtable':lenhtable,'history_search_table':history_search_table,'model_manager_form':model_manager_form})

def tram_table(request,no_return_httpresponse = False): # include search tram 
    print 'tram_table'
    if 'id' in request.GET:
        id = request.GET['id']
        querysets =[]
        kq_searchs_one_contain = Table3g.objects.get(id=id)
        querysets.append(kq_searchs_one_contain)
        query = request.GET['query']
        save_history(query)
    elif 'query' not in request.GET and 'id' not in request.GET or (request.GET['query']=='')  : # khong search, khong chose , nghia la querysets khi load page index
        querysets = Table3g.objects.all()
    elif 'query' in request.GET : # tuc la if request.GET['query'], nghia la dang search:
        query = request.GET['query']
        print 'this mine',query
        if '&' in query:
            contains = request.GET['query'].split('&')
            query_sign = 'and'
        else:
            contains = request.GET['query'].split(',')
            query_sign = 'or'
        kq_searchs = Table3g.objects.none()
        for count,contain in enumerate(contains):
            fname_contain_reconize_tuple = recognize_fieldname_of_query(contain,MYD4_LOOKED_FIELD)#return (longfieldname, searchstring)
            contain = fname_contain_reconize_tuple[1]
            print 'contain',contain
            fieldnameKey = fname_contain_reconize_tuple[0]
            print 'fieldnameKey',fieldnameKey
            if fieldnameKey=="all field":
                    FNAME = [f.name for f in Table3g._meta.fields if isinstance(f, CharField)]
                    qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: contain}) for fieldname in FNAME ))
                    FRNAME = [f.name for f in Table3g._meta.fields if (isinstance(f, ForeignKey) or isinstance(f, ManyToManyField))]
                    print 'FRNAME',FRNAME
                    Many2manyfields =[f.name for f in Table3g._meta.many_to_many]
                    print 'Many2manyfields',Many2manyfields
                    FRNAME  = FRNAME + Many2manyfields
                    qgroup_FRNAME = reduce(operator.or_, (Q(**{"%s__Name__icontains" % fieldname: contain}) for fieldname in FRNAME ))
                    qgroup = qgroup | qgroup_FRNAME
            else:
                print 'fieldnameKey %s,contain%s'%(fieldnameKey,contain)
                qgroup = Q(**{"%s__icontains" % fieldnameKey: contain})
            if not fname_contain_reconize_tuple[2]:#neu khong query phu dinh
                kq_searchs_one_contain = Table3g.objects.filter(qgroup)
            else:
                kq_searchs_one_contain = Table3g.objects.exclude(qgroup)
            if query_sign=="or": #tra nhieu tram.
                kq_searchs = list(chain(kq_searchs, kq_searchs_one_contain))
            elif query_sign=="and": # dieu kien AND but loop all field with or condition
                if count==0:
                    kq_searchs = kq_searchs_one_contain
                else:
                    kq_searchs = kq_searchs & kq_searchs_one_contain
        querysets = kq_searchs
        print 'len(querysets)',len(querysets)    
        #save_history(query)    
    
    if no_return_httpresponse:
        return querysets
    else:
        table = Table3gTable(querysets,) 
        dict_context = {'table': table}
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        return render(request, 'drivingtest/custom_table_template_mll.html', dict_context)
#URL  =  $.get('/omckv2/search_history/'
# DELETE SOMETHING ON SURFACE AND C          
class FilterToGenerateQ():
    def __init__(self,request,FormClass,ModelClass,form_cleaned_data,No_AUTO_FILTER_FIELDS=[]):
        self.form_cleaned_data = form_cleaned_data
        self.EXCLUDE_FIELDS = getattr(FormClass.Meta,'exclude', [])
        self.No_AUTO_FILTER_FIELDS = No_AUTO_FILTER_FIELDS
        self.ModelClass = ModelClass
        self.request = request
    def generateQgroup(self):
        qgroup=Q()
        #CHARFIELDS = []
        for f in self.ModelClass._meta.fields :
            try:
                if not self.request.GET[f.name] or  (f.name  in self.EXCLUDE_FIELDS) or  (f.name  in self.No_AUTO_FILTER_FIELDS):
                    continue
            except :#MultiValueDictKeyError
                continue
            functionname = 'generate_qobject_for_exit_model_field_'+f.name
            no_auto_function = getattr(self, functionname,None)
            print ('functionname, f',functionname,no_auto_function)
            if no_auto_function:
                g_no_auto = no_auto_function(f.name)
                qgroup &=g_no_auto
            elif isinstance(f,CharField):
                qgroup &=Q(**{'%s__icontains'%f.name:self.form_cleaned_data[f.name]})
            elif isinstance(f,DateTimeField):
                pass
            else:
                qgroup &=Q(**{'%s'%f.name: self.form_cleaned_data[f.name]})
        #MANYTOMANYFIELDS 
        for f in self.ModelClass._meta.many_to_many :
            try:
                if not self.request.GET[f.name]:
                    continue
            except :#MultiValueDictKeyError
                continue
            print '****many to manu self.form_cleaned_data[f.name]',self.form_cleaned_data[f.name]
            if (f.name not in self.EXCLUDE_FIELDS) and (f.name not in self.No_AUTO_FILTER_FIELDS):
                qgroup &=Q(**{'%s__in'%f.name:self.form_cleaned_data[f.name]})
        q_out_field = getattr(self,'generate_qobject_for_NOT_exit_model_fields',None)
        if q_out_field:
            q_outer_field = self.generate_qobject_for_NOT_exit_model_fields()
            qgroup &= q_outer_field       
        return qgroup     
    
   
    
class FilterToGenerateQ_ForMLL(FilterToGenerateQ):
    def generate_qobject_for_exit_model_field_gio_mat(self,fname):
            d = self.form_cleaned_data[fname]
            print 'ddfdddddd',d
            q_gio_mat = Q(gio_mat__lte=d)
            return q_gio_mat
    def generate_qobject_for_NOT_exit_model_fields(self):
        qgroup=Q()
        if self.request.GET['comment']:
            q_across = Q(comments__comment__icontains=self.request.GET['comment'])
            qgroup = qgroup&q_across
        if self.request.GET['specific_problem_m2m']:
            q_across_fault = Q(specific_problems__fault__Name__icontains=self.request.GET['specific_problem_m2m'])
            q_across_object_name = Q(specific_problems__object_name__icontains=self.request.GET['specific_problem_m2m'])
            q_specific_problem_m2m = q_across_fault | q_across_object_name
            qgroup = qgroup & q_specific_problem_m2m
        if self.form_cleaned_data['doi_tac']: # input text la 1 doi tac hoan chinh nhu la a-b-number
            print 'afddfdfdf',self.form_cleaned_data['doi_tac']
            q_across_doi_tac = Q(comments__doi_tac=self.form_cleaned_data['doi_tac'])
            qgroup = qgroup & q_across_doi_tac
        elif self.request.GET['doi_tac']: # input text la form
            fieldnames = [f.name for f in Doitac._meta.fields if isinstance(f, CharField)]
            q_across_doi_tac = reduce(operator.or_, (Q(**{"comments__doi_tac__%s__icontains" % fieldname: self.request.GET['doi_tac']}) for fieldname in fieldnames ))
            print '***********@@'
            #q_across_doi_tac = Q(**{"comments__doi_tac__%s__icontains" % 'Full_name': self.request.GET['doi_tac']})
            qgroup = qgroup & q_across_doi_tac
        return qgroup
    
def prepare_value_for_specificProblem(specific_problem_instance):
    return ((specific_problem_instance.fault.Name + '**') if specific_problem_instance.fault else '') + ((specific_problem_instance.object_name) if specific_problem_instance.object_name else '')
# delete surface branch

def update_trang_thai_cho_mll(mll_instance):
    last_comment_instance = mll_instance.comments.latest('id')
    mll_instance.trang_thai = last_comment_instance.trang_thai
    mll_instance.save()                                               
#MODAL_style_title_dict_for_form = {'CommentForMLLForm':('')}
def modelmanager(request,form_name,entry_id):
    status_code = 200
    url = '/omckv2/modelmanager/'+ form_name +'/'+entry_id+'/'
    try:
        form_table_template =request.GET['form-table-template']
    except:
        form_table_template = 'normal form template'
    try:
        which_form_or_table = request.GET['which-form-or-table']
    except:
        which_form_or_table = 'table only'
    ModelClass_name = re.sub('Form$','',form_name,1)
    dict_render ={}
    need_valid=False
    need_save_form  =False
    data=None
    initial=None
    instance=None
    form_notification = None
    table_notification = '<h2 class="table_notification"> Danh sach duoc hien thi o table phia duoi</h2>'
    loc = True if 'loc' in request.GET else False
    is_download = True if 'downloadtable' in request.GET else False
    loc_pass_agrument=False
    is_allow_edit=False
    #is_download_csv = True if 'table-'
    #print '@@@@@@@@@@@@222 table_to_csv',is_download_csv
    if which_form_or_table!="table only" or loc or (is_download and loc): #get Form Class
        if request.method=='POST':
            need_valid =True
            need_save_form=True
            data = request.POST
            loc_pass_agrument = False
        
        elif loc:
            need_valid =True
            data = request.GET
            loc_pass_agrument = True
        
        FormClass = eval('forms.' + form_name)#repeat same if loc
        ModelClass = FormClass.Meta.model # repeat same if loc
        
        #Initial form
        if entry_id=='new':
            if request.method =='GET':
                # special form is CommentForMLLForm, must give a initial in new form,rest just create new form
                if form_name =='CommentForMLLForm':
                    initial = {'mll':request.GET['selected_instance_mll']}
                    #form = FormClass(data=data,form_table_template=form_table_template,initial=intial_form)#form_table_template dua vao form de xac dinh cac button
                #else:
                    #form = FormClass(data=data,form_table_template=form_table_template,initial=initial)
                form_notification = u'<h2 class="form-notification text-primary"> Form ready</h2>'
        else: #isinstance(id,int)
            instance = ModelClass.objects.get(id = entry_id)
            
            if request.method =='GET':
                if form_name == 'MllForm':
                    specific_problem_m2m_value = '\n'.join(map(prepare_value_for_specificProblem,instance.specific_problems.all()))
                    initial = {'specific_problem_m2m':specific_problem_m2m_value} 
                #elif form_name =='Table3g_NTPForm'
                if 'is_allow_edit' in request.GET:
                    is_allow_edit=True # chuc nang cua is_allow_edit la de display nut edit hay khong
                    #form = FormClass(data=data,instance = instance,form_table_template=form_table_template,is_allow_edit=is_allow_edit )
                form_notification = u'<h2 class="form-notification text-warning">Ready for edit for item has ID %s</h2>'%entry_id
        #init a form
        form = FormClass(data=data,instance = instance,initial=initial,loc =loc_pass_agrument,form_table_template=form_table_template,is_allow_edit=is_allow_edit,request = request )
        #form.update_action_and_button(url)
        if need_save_form and entry_id !="new": # lay gia tri cu can thiet cho 1 so form truoc khi valid form hoac save
            if form_name=="MllForm":
                thanh_vien_old = instance.thanh_vien 
        if need_valid:
            
            is_form_valid = form.is_valid()
            if not is_form_valid :
                #dict_render.update({'form_notification':u'<h2 class="form-notification text-danger">nhap form sai,vui long check lai </h2>'})
                form_notification = u'<h2 class="form-notification text-danger">nhap form sai,vui long check lai </h2>'
                status_code = 400
        if need_save_form and status_code !=400:
            if form_name=="MllForm":
                now = datetime.now()
                if entry_id =="new":
                    instance = form.save(commit=False)
                    mll_instance= instance
                    user = request.user
                    mll_instance.thanh_vien = user
                    mll_instance.ca_truc = user.get_profile().ca_truc
                else:#Edit mll
                    instance = form.save(commit=False)
                    mll_instance=instance
                    mll_instance.thanh_vien = thanh_vien_old
                    mll_instance.last_edit_member = request.user
                    mll_instance.edit_reason = request.GET['edit_reason']
                    '''
                    if (EditHistory.objects.all().count() > 10 ):
                        oldest_instance= EditHistory.objects.all().order_by('search_datetime')[0]
                        oldest_instance.ly_do_sua = request.GET['edit_reason']
                        oldest_instance.search_datetime = now
                        oldest_instance.tram = mll_instance
                        oldest_instance.save()
                    else:
                        instance_ehis = EditHistory(ly_do_sua = request.GET['edit_reason'],search_datetime = now,tram = mll_instance )
                        instance_ehis.save()
                    '''
                    update_trang_thai_cho_mll(mll_instance)
                
                mll_instance.last_update_time = now
                mll_instance.save()# save de tao nhung cai database relate nhu foreinkey.
                
                # luu specific_problem_m2m
                specific_problem_m2ms = form.cleaned_data['specific_problem_m2m'].split('\n')
                for count,specific_problem_m2m in enumerate(specific_problem_m2ms):
                    if '**' in specific_problem_m2m:
                        faulcode_hyphen_objects = specific_problem_m2m.split('**')
                        faultLibrary_instance = FaultLibrary.objects.get_or_create(Name = faulcode_hyphen_objects[0])[0] # dung de gan (fault = faultLibrary_instance)
                        if len(faulcode_hyphen_objects) > 1:
                            object_name = faulcode_hyphen_objects[1]
                        else:
                            object_name=None
                    else:
                        faultLibrary_instance = None
                        object_name = specific_problem_m2m
                    if entry_id =="new":
                        SpecificProblem.objects.create(fault = faultLibrary_instance, object_name = object_name,mll=mll_instance)
                    else:#ghi chong len nhung entry problem specific dang co
                        specific_problems = mll_instance.specific_problems.all()
                        try:
                            specific_problem = specific_problems[count]
                            print 'current specific_problems',specific_problem.object_name
                            specific_problem.fault = faultLibrary_instance
                            specific_problem.object_name = object_name
                            specific_problem.save()
                        except IndexError: # neu thieu instance hien tai so voi nhung instance sap duoc ghi thi tao moi 
                            SpecificProblem.objects.create(fault = faultLibrary_instance, object_name = object_name,mll=mll_instance)
                        # delete nhung cai specific_problems khong duoc ghi chong
                        if (len(specific_problems) > count): 
                            for x in specific_problems[count+1:]:
                                x.delete()
                
                # luu CommentForMLLForm
                if entry_id =="new":
                    CommentForMLLForm_i = CommentForMLLForm(request.POST)
                    if CommentForMLLForm_i.is_valid():
                        print "CommentForMLLForm_i['datetime']",CommentForMLLForm_i.cleaned_data['datetime']
                        first_comment = CommentForMLLForm_i.save(commit=False)
                        first_comment.thanh_vien = user
                        first_comment.mll = mll_instance
                        first_comment.save()
                    else:
                        return HttpResponseBadRequest('khong valid',CommentForMLLForm_i.errors.as_text())
                
                #RELOad new form
                specific_problem_m2m_value = '\n'.join(map(prepare_value_for_specificProblem,mll_instance.specific_problems.all()))
                initial = {'specific_problem_m2m':specific_problem_m2m_value} 
                form = MllForm(instance=mll_instance,initial=initial,request=request)
               
            elif form_name=="CommentForMLLForm":
                instance = form.save(commit=False)
                if entry_id =="new":
                        comment_instance = instance
                        mll_instance  = Mll.objects.get(id=request.POST['mll'])
                        comment_instance.mll = mll_instance
                else:
                    comment_instance = instance
                    olddatetime = comment_instance.datetime
                    if not request.POST['datetime']:
                        comment_instance.datetime = olddatetime
                comment_instance.thanh_vien = request.user
                comment_instance.save()
                form.save_m2m() 
                if form.cleaned_data['trang_thai'].is_cap_nhap_gio_tot:
                    mll_instance.gio_tot = form.cleaned_data['datetime']
                    mll_instance.save()
                if form.cleaned_data['trang_thai'].Name==u'Báo ứng cứu':
                    mll_instance.ung_cuu = True
                    mll_instance.save() 
            elif form_name=="Table3g_NTPForm":
                form.save(commit=True)
                if (request.GET['update_all_same_vlan_sites']=='yes'):
                    rnc = instance.RNC
                    IUB_VLAN_ID = instance.IUB_VLAN_ID
                    same_sites = Table3g.objects.filter(RNC=rnc,IUB_VLAN_ID=IUB_VLAN_ID)
                    same_sites.update(**dict([(fn,request.POST[fn])for fn in NTP_Field]))
            
            else:
                instance = form.save(commit=True)
            
            #update history edit
            if ( entry_id !="new" and (form_name=="Table3gForm" or form_name == 'MllForm')):
                if (EditHistory.objects.all().count() > 100 ):
                        oldest_instance= EditHistory.objects.all().order_by('edit_datetime')[0]
                        oldest_instance.ly_do_sua = request.GET['edit_reason']
                        oldest_instance.search_datetime = datetime.now()
                        oldest_instance.edited_object_id = instance.id
                        oldest_instance.modal_name = ModelClass_name
                        oldest_instance.save()
                else:
                    instance_ehis = EditHistory(modal_name = ModelClass_name, ly_do_sua = request.GET['edit_reason'],edit_datetime = datetime.now(),edited_object_id = instance.id )
                    instance_ehis.save()
                    
                    
            # update form notifcation only for normal form not for modal form
            if form_table_template =='normal form template':
                if entry_id =="new":
                    id_string =  str(instance.id)
                    url = '/omckv2/modelmanager/'+ form_name +'/'+ id_string+'/'
                    form_notification = u'<h2 class="form-notification text-success">You have been created an item has id %s,continue with edit</h2>'%id_string
                else:
                    form_notification = u'<h2 class="form-notification text-success">successfully,You have been edited an item has id %s,continue with edit</h2>'%entry_id
            #reload form with newinstance
            if form_name != 'MllForm':
                form = FormClass(instance = instance,request=request)###############3
        if not is_download:
            form.update_action_and_button(url)        
            dict_render = {'form':form,'form_notification':form_notification}        
        
    #TABLE
    if (which_form_or_table!="form only" and status_code == 200) or is_download:
        if 'table_name' in request.GET:
            TableClass = eval('forms.' + request.GET['table_name'])
            ModelClass = TableClass.Meta.model
            ModelClass_name = re.sub('Table','',request.GET['table_name'],1)
        else:
            TableClass = eval('forms.' + re.sub('Form$','Table',form_name))
        if which_form_or_table=="table only" :# can phai lay ModelClass neu phia neu chua lay form
            ModelClass = TableClass.Meta.model

        if 'table3gid' in request.GET:
                querysets =[]
                kq_searchs_one_contain = ModelClass.objects.get(id=request.GET['table3gid'])
                if form_name =='Table3gForm':
                    save_history(kq_searchs_one_contain.site_name_1,request)
                querysets.append(kq_searchs_one_contain)
                table_notification = '<h2 class="table_notification"> Tram duoc chon cung duoc hien thi o table phia duoi</h2>'
        elif 'query_main_search_by_button' in request.GET:
            query = request.GET['query_main_search_by_button']
            if '&' in query:
                contains = request.GET['query_main_search_by_button'].split('&')
                query_sign = 'and'
            else:
                contains = request.GET['query_main_search_by_button'].split(',')
                query_sign = 'or'
            kq_searchs = Table3g.objects.none()
            for count,contain in enumerate(contains):
                fname_contain_reconize_tuple = recognize_fieldname_of_query(contain,MYD4_LOOKED_FIELD)#return (longfieldname, searchstring)
                contain = fname_contain_reconize_tuple[1]
                print 'contain',contain
                fieldnameKey = fname_contain_reconize_tuple[0]
                print 'fieldnameKey',fieldnameKey
                if fieldnameKey=="all field":
                        FNAME = [f.name for f in Table3g._meta.fields if isinstance(f, CharField)]
                        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: contain}) for fieldname in FNAME ))
                        
                        FRNAME = [f.name for f in Table3g._meta.fields if (isinstance(f, ForeignKey) or isinstance(f, ManyToManyField))]
                        print 'FRNAME',FRNAME
                        Many2manyfields =[f.name for f in Table3g._meta.many_to_many]##
                        print 'Many2manyfields',Many2manyfields
                        FRNAME  = FRNAME + Many2manyfields
                        if FRNAME:
                            qgroup_FRNAME = reduce(operator.or_, (Q(**{"%s__Name__icontains" % fieldname: contain}) for fieldname in FRNAME ))
                            qgroup = qgroup | qgroup_FRNAME
                else:
                    qgroup = Q(**{"%s__icontains" % fieldnameKey: contain})
                if not fname_contain_reconize_tuple[2]:#neu khong query phu dinh
                    kq_searchs_one_contain = Table3g.objects.filter(qgroup)
                else:
                    kq_searchs_one_contain = Table3g.objects.exclude(qgroup)
                if query_sign=="or": #tra nhieu tram.
                    kq_searchs = list(chain(kq_searchs, kq_searchs_one_contain))
                elif query_sign=="and": # dieu kien AND but loop all field with or condition
                    if count==0:
                        kq_searchs = kq_searchs_one_contain
                    else:
                        kq_searchs = kq_searchs & kq_searchs_one_contain
            querysets = kq_searchs
            print 'len(querysets)',len(querysets)    
            table_notification = '<h2 class="table_notification"> tim kiem  %s trong database %s duoc hien thi o table phia duoi</h2>'%(query,ModelClass_name)
        elif 'query_main_search_by_manager_button' in request.GET:
            query = request.GET['query_main_search_by_manager_button']
            if '&' in query:
                contains = request.GET['query_main_search_by_manager_button'].split('&')
                query_sign = 'and'
            else:
                contains = request.GET['query_main_search_by_manager_button'].split(',')
                query_sign = 'or'
            kq_searchs = ModelClass.objects.none()
            for count,contain in enumerate(contains):
                fname_contain_reconize_tuple = recognize_fieldname_of_query(contain,MYD4_LOOKED_FIELD)#return (longfieldname, searchstring)
                contain = fname_contain_reconize_tuple[1]
                print 'contain**manager',contain
                fieldnameKey = fname_contain_reconize_tuple[0]
                print 'fieldnameKey',fieldnameKey
                if fieldnameKey=="all field":
                        FNAME = [f.name for f in ModelClass._meta.fields if isinstance(f, CharField)]
                        print 'FNAME',FNAME
                        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: contain}) for fieldname in FNAME ))
                        FRNAME = [f.name for f in ModelClass._meta.fields if (isinstance(f, ForeignKey) or isinstance(f, ManyToManyField))]
                        print 'FRNAME',FRNAME
                        Many2manyfields =[f.name for f in ModelClass._meta.many_to_many]
                        print 'Many2manyfields',Many2manyfields
                        FRNAME  = FRNAME + Many2manyfields
                        if FRNAME:
                            qgroup_FRNAME = reduce(operator.or_, (Q(**{"%s__Name__icontains" % fieldname: contain}) for fieldname in FRNAME ))
                            qgroup = qgroup | qgroup_FRNAME
                else:
                    qgroup = Q(**{"%s__icontains" % fieldnameKey: contain})
                if not fname_contain_reconize_tuple[2]:#neu khong query phu dinh
                    kq_searchs_one_contain = ModelClass.objects.filter(qgroup)
                else:
                    kq_searchs_one_contain = ModelClass.objects.exclude(qgroup)
                if query_sign=="or": #tra nhieu tram.
                    kq_searchs = list(chain(kq_searchs, kq_searchs_one_contain))
                elif query_sign=="and": # dieu kien AND but loop all field with or condition
                    if count==0:
                        kq_searchs = kq_searchs_one_contain
                    else:
                        kq_searchs = kq_searchs & kq_searchs_one_contain
            querysets = kq_searchs
            print 'len(querysets)',len(querysets)    
            table_notification = '<h2 class="table_notification"> tim kiem  %s trong database %s duoc hien thi o table phia duoi</h2>'%(query,ModelClass_name)
        
        elif form_name =='Table3g_NTPForm':
            if 'tram_id_for_same_ntp' in request.GET : #da la cai nay thi khong the co loc trong , khi click vao download script 
                instance_site = Table3g.objects.get(id = request.GET['tram_id_for_same_ntp'])
                rnc = instance_site.RNC
                IUB_VLAN_ID = instance_site.IUB_VLAN_ID
                querysets = Table3g.objects.filter(RNC=rnc,IUB_VLAN_ID=IUB_VLAN_ID)
                print 'len(querysets)',len(querysets)
        elif form_name =='EditHistoryForm':
            tram_id = request.GET['tram_id']
            tram_instance = Table3g.objects.get(id = tram_id)
            querysets = EditHistory.objects.filter(tram = tram_instance)
        elif loc:
            if request.method =='POST':# submit form name khong cung model class voi table nam, trong truong hop submit form o modal va lam thay doi mlltable
                print 'form_table_template',form_table_template
                if 'table_name' in request.GET:
                    form_name =  re.sub('Table$','Form',request.GET['table_name'])
                    FormClass= eval('forms.' + form_name)
                    print '@@@@@FormClass',FormClass
                
                
                form = FormClass(data=request.GET,loc=True)
                if form.is_valid():#alway valid but you must valid to get form.cleaned_data:
                    print '######form cua get loc valid'
                else:
                    print 'form.errors',form.errors.as_text()
            if form_name=='MllForm':
                FiterClass=FilterToGenerateQ_ForMLL # adding more out field fiter
            else:
                FiterClass= FilterToGenerateQ
            
            qgroup_instance= FiterClass(request,FormClass,ModelClass,form.cleaned_data)
            qgroup = qgroup_instance.generateQgroup()
            querysets = ModelClass.objects.filter(qgroup).distinct().order_by('-id')
            if request.method !='POST':
                form_notification =u'<h2 class="form-notification text-info">  Số kết quả lọc là %s trong database %s<h2>'%(len(querysets),form_name.replace('Form',''))
            loc_query = ''
            count=0
            for k,f in form.fields.items():
                try:
                    v = request.GET[k]
                except:
                    continue
                if v:
                    try:
                        label = f.label +''
                    except TypeError:
                        label = k
                    count +=1
                    if count==1:
                        print '$#@#$#$#fname',k
                        loc_query = label + '=' + v
                        
                    else:
                        loc_query = loc_query + '&'+label + '=' + v 
            table_notification = '<h2 class="table_notification"> ket qua loc  cua chuoi %s trong database %s duoc hien thi o table phia duoi</h2>'%(loc_query,ModelClass_name)

        
        else: # if !loc and ...
            querysets = ModelClass.objects.all().order_by('-id')
            table_notification = '<h2 class="table_notification"> Tat ca record trong database %s duoc hien thi o table phia duoi</h2>'%ModelClass_name
        if status_code != 400:
            table = TableClass(querysets) # vi query set cua form_name=="Table3gForm" and entry_id !='new' khong order duoc nen phai tach khong di lien voi t
            RequestConfig(request, paginate={"per_page": 15}).configure(table)
            dict_render.update({'table':table,'form_notification':form_notification,'table_notification':table_notification})
    if 'downloadtable' in request.GET:
        if request.GET['downloadtable'] == 'csv':
            return table.as_xls_d4_in_form_py_csv(request)
        elif request.GET['downloadtable'] == 'xls':
            return table.as_xls_d4_in_form_py_xls(request)
    if form_table_template =='form on modal' and which_form_or_table !='table only':# and not click order-sort
        return render(request, 'drivingtest/form_table_manager_for_modal.html',dict_render,status=status_code)
    else:
        return render(request, 'drivingtest/form_table_manager.html',dict_render,status=status_code)
            



def download_script_ntp(request):
    sendmail=0
    site_id = request.GET['site_id']
    print 'site_id',site_id
    instance_site = Table3g.objects.get(id=site_id)
    sitename = instance_site.site_id_3g
    if not sitename:
        return HttpResponseBadRequest('khong ton tai site 3G cua tram nay')
    tao_script= tao_script_r6000_w12( instance_site,ntpServerIpAddressPrimary = request.GET['ntpServerIpAddressPrimary'],\
                              ntpServerIpAddressSecondary= request.GET['ntpServerIpAddressSecondary'],\
                               ntpServerIpAddress1= request.GET['ntpServerIpAddress1'],\
                                ntpServerIpAddress2 = request.GET['ntpServerIpAddress2'])
    if tao_script[0]:
        file_names = tao_script[0]
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        for file_name in  file_names:
            filename = settings.MEDIA_ROOT + '/for_user_download_folder/' + file_name # Select your file here.                              
            archive.write(filename, ntpath.basename(filename))
        archive.close()
    else: # neu khong co list file, tuc la tao_script_r6000_w12 da tao file zip roi
        temp = tao_script[1]
    loai_tu = tao_script[2]
    basename = sitename+"_"+ loai_tu +'.zip'
    if sendmail:
        send_email(files= temp,filetype='tempt',fname = basename)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%(basename)
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response 

def edit_history_search(request):
    
    try:
        id_h = request.GET['history_search_id']
        try:
            print 'id_h',id_h
            instance = SearchHistory.objects.get(id=int(id_h))
        except:
            print 'loi tai instance nay'
        if request.GET['action']=="edit":
            #instance = SearchHistory.objects.get(id=id_h)
            print request.GET
            for f in H_Field:
                if f in request.GET:
                    value = request.GET[f] 
                    if value!= u'—':
                        setattr(instance,f,value)
                        instance.save()
                        history_search_table = SearchHistoryTable(SearchHistory.objects.all().order_by('-search_datetime'), )
        else:
            
            instance.delete()
            #request.session.flush()
        history_search_table = SearchHistoryTable(SearchHistory.objects.all().order_by('-search_datetime'), )
        RequestConfig(request, paginate={"per_page": 10}).configure(history_search_table)
        return render(request, 'drivingtest/custom_table_template_mll.html',{'table':history_search_table})           
    except Exception as e:
        print type(e),e
        return HttpResponse(str(e))
from django.template import Template 



def description_for_search_tram_autocomplete(tram,*args):
    output =''
    last_index = len(args) -1 
    for count, fieldname in enumerate(args):
        value = getattr(tram,fieldname)
        sortname =  MYD4_LOOKED_FIELD[fieldname]
        output += '<span class="tram_field_name">'+sortname+ ': ' +'</span>'+ (value if value else '___' )+ (' , ' if not count==last_index else '') 
    return output        
def autocomplete (request):
    print request.GET
    query   = request.GET['query'].lstrip().rstrip()
    print 'ban dang search',query
    name_attr = request.GET['name_attr']
    results = [] # results la 1 list gom nhieu dict, moi dict la moi li , moi dict la moi ket qua tim kiem
    if name_attr =='nguyen_nhan':
        fieldnames = [f.name for f in Nguyennhan._meta.fields if isinstance(f, CharField)  ]
        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: query}) for fieldname in fieldnames ))
        doitac_querys = Nguyennhan.objects.filter(qgroup)
        for doitac in doitac_querys[:10]:
            doitac_dict = {}
            doitac_dict['label'] = doitac.Name 
            doitac_dict['desc'] = doitac.Ghi_chu  if doitac.Ghi_chu else ''
            results.append(doitac_dict)
        to_json = {
            "key_for_list_of_item_dict": results,
        }
    elif name_attr =='manager_suggestion':
        modelClass = eval('models.'+request.GET['model_attr_global'])
        fieldnames = [f.name for f in modelClass._meta.fields if isinstance(f, CharField)  ]
        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: query}) for fieldname in fieldnames ))
        querys = modelClass.objects.filter(qgroup)
        for object in querys[:10]:
            object_dict = {}
            object_dict['label'] = object.__unicode__()
            object_dict['id'] = object.id
            object_dict['desc'] = ''
            results.append(object_dict)
        to_json = {
            "key_for_list_of_item_dict": results,
        }
        
    elif name_attr =='du_an':
        fieldnames = [f.name for f in Duan._meta.fields if isinstance(f, CharField)  ]
        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: query}) for fieldname in fieldnames ))
        doitac_querys = Duan.objects.filter(qgroup)
        for doitac in doitac_querys[:10]:
            doitac_dict = {}
            doitac_dict['label'] = doitac.Name 
            doitac_dict['desc'] =  ''
            results.append(doitac_dict)
        to_json = {
            "key_for_list_of_item_dict": results,
        }
    elif 'trang_thai' in name_attr:
        fieldnames = [f.name for f in TrangThaiCuaTram._meta.fields if isinstance(f, CharField)  ]
        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: query}) for fieldname in fieldnames ))
        doitac_querys = TrangThaiCuaTram.objects.filter(qgroup)
        for doitac in doitac_querys[:10]:
            doitac_dict = {}
            doitac_dict['label'] = doitac.Name 
            doitac_dict['desc'] =  ''
            results.append(doitac_dict)
        to_json = {
            "key_for_list_of_item_dict": results,
        }
    elif 'specific_problem_m2m' in name_attr:
        qgroup = Q(Name__icontains=query)
        doitac_querys = FaultLibrary.objects.filter(qgroup)
        for doitac in doitac_querys[:10]:
            doitac_dict = {}
            doitac_dict['label'] = doitac.Name 
            doitac_dict['desc'] =  ''
            results.append(doitac_dict)
        to_json = {
            "key_for_list_of_item_dict": results,
        } 
    elif name_attr =='doi_tac' :
        fieldnames = [f.name for f in Doitac._meta.fields if isinstance(f, CharField)  ]
        if '-' not in query:
            print 'fieldnames',fieldnames
            qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: query}) for fieldname in fieldnames ))
            doitac_querys = Doitac.objects.filter(qgroup).distinct()
            print len(doitac_querys)
            for doitac in doitac_querys[:10]:
                doitac_dict = {}
                doitac_dict['label'] = doitac.Full_name + ("-" + doitac.Don_vi if doitac.Don_vi else "") 
                doitac_dict['desc'] = doitac.So_dien_thoai if doitac.So_dien_thoai else 'chưa có sdt'
                results.append(doitac_dict)
            to_json = {
                "key_for_list_of_item_dict": results,
            }
        else:# there '-' in query
            contains = query.split('-')
            for count,contain in enumerate(contains):
                qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: contain}) for fieldname in fieldnames))
                kq_searchs_one_contain = Doitac.objects.filter(qgroup)
                if count==0:
                    kq_searchs = kq_searchs_one_contain
                else:
                    kq_searchs = kq_searchs & kq_searchs_one_contain    
            for doitac in kq_searchs[:10]:
                doitac_dict = {}
                doitac_dict['value'] = doitac.id
                doitac_dict['label'] = doitac.Full_name + "-" + doitac.Don_vi
                doitac_dict['desc'] = doitac.So_dien_thoai if doitac.So_dien_thoai else 'chưa có sdt'
                results.append(doitac_dict)
            to_json = {
                "key_for_list_of_item_dict": results,
            }
    elif name_attr =='subject' or name_attr =="main_suggestion":
        contain = query
        if contain =='':
            fieldnames = {'site_id_3g':'3G'}
        else:
            fieldnames = MYD4_LOOKED_FIELD
        
        for fieldname,sort_fieldname  in fieldnames.iteritems(): #Loop through all field
            q_query = Q(**{"%s__icontains" % fieldname: contain})
            one_kq_searchs = Table3g.objects.filter(q_query)[0:20]
            if len(one_kq_searchs)>0:
                for tram in one_kq_searchs:
                    tram_dict = {}
                    try:
                        if fieldname =="site_id_3g":
                            thiet_bi = str(tram.Cabinet)
                        elif fieldname =="site_ID_2G":
                            thiet_bi =str(tram.nha_san_xuat_2G)
                        else:
                            thiet_bi = "2G&3G"
                    except Exception as e:
                            thiet_bi = 'error' + tram.site_name_1
                            #print e, tram
                    tram_dict['id'] = tram.id
                    tram_dict['sort_field'] = sort_fieldname
                    tram_dict['label'] =  getattr(tram,fieldname)
                    tram_dict['thiet_bi'] =  thiet_bi
                    tram_dict['site_name_1'] = tram.site_name_1
                    tram_dict['desc'] = description_for_search_tram_autocomplete(tram ,'site_name_1','site_name_2',)
                    tram_dict['desc2'] = description_for_search_tram_autocomplete(tram ,'site_id_3g','site_ID_2G')
                    results.append(tram_dict)
        to_json = {
                "key_for_list_of_item_dict": results,
            }
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

def render_table_mll(request):
    table = MllTable(Mll.objects.all().order_by('-id'))
    RequestConfig(request, paginate={"per_page": 15}).configure(table)        
    return render(request, 'drivingtest/custom_table_template.html',{'table':table})
def delete_mll (request):
    id = request.GET['query']
    mll_instance  = Mll.objects.get(id=int(id))
    mll_instance.comments.all().delete()
    mll_instance.delete()
    return render_table_mll(request)
from django.core.servers.basehttp import FileWrapper

def search_history(request):
    history_search_table = SearchHistoryTable(SearchHistory.objects.all().order_by('-search_datetime'), )
    RequestConfig(request, paginate={"per_page": 10}).configure(history_search_table)
    return render(request, 'drivingtest/custom_table_template_mll.html',{'table':history_search_table})


def save_history(query,request):
    if (SearchHistory.objects.filter(thanh_vien=request.user).count() > 3 ):
                oldest_instance= SearchHistory.objects.all().order_by('search_datetime')[0]
                oldest_instance.query_string = query
                oldest_instance.search_datetime = datetime.now()
                oldest_instance.thanh_vien = request.user
                oldest_instance.save()
    else:
        instance = SearchHistory(query_string=query,search_datetime = datetime.now(),thanh_vien = request.user)
        instance.save()


def suggestion(request):
        print 'suggestion'
        context = RequestContext(request)
        if request.method == 'GET':
                contain = request.GET['query']
                if contain =='':
                    fieldnames = {'site_id_3g':'3G'}
                else:
                    fieldnames = MYD4_LOOKED_FIELD
        print 'ban dan search',contain
        recognize = recognize_fieldname_of_query(contain, fieldnames)
        dicta ={}    
        for fieldname,sort_fieldname  in fieldnames.iteritems():
            q_query = Q(**{"%s__icontains" % fieldname: contain})
            one_kq_search = Table3g.objects.filter(q_query)[0:20]
            if len(one_kq_search)>0:
                dicta[sort_fieldname] = [fieldname,one_kq_search]
        context_dict = {'dict':dicta}
                
        return render_to_response('drivingtest/kq_searchs.html', context_dict, context)        

def lenh_suggestion(request):
    if request.method == 'GET':
            contain = request.GET['query']
    fieldnames = [f.name for f in Command3g._meta.fields if isinstance(f, CharField)]
    print 'fname',fieldnames
    try:
        qgroup = reduce(operator.or_, (Q(**{"%s__icontains" % fieldname: contain}) for fieldname in fieldnames))
        kq_searchs = Command3g.objects.filter(qgroup)
        #context_dict = {'kq_searchs':kq_searchs}
    except Exception as e:
        print 'loi trong queyry',type(e),e    
    table = Command3gTable(kq_searchs,)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    return render(request, 'drivingtest/custom_table_template_mll.html', {'table': table})



@login_required
def upload_excel_file1(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result_handle_file ="form is valid"
            choices =  form.cleaned_data['sheetchoice']
            is_available_file =  form.cleaned_data['is_available_file']
            if not is_available_file: # Neu khong tick vao cai o chon file co san
                if 'file' in request.FILES:
                    fcontain = request.FILES['file'].read()
                    workbook = xlrd.open_workbook(file_contents=fcontain)
                    import_database_4_cai_new(choices,workbook = workbook,is_available_file=False)
                else: # but not file upload so render invalid
                    result_handle_file = 'Invalid choices, please select file or tick into "is_available_file"'
                    return render_to_response('drivingtest/upload_excel_file.html', {'form': form,'result_handle_file':result_handle_file},context)
            else:
                import_database_4_cai_new(choices,workbook = None,is_available_file=is_available_file)
            return render_to_response('drivingtest/upload_excel_file.html', {'form': form,'result_handle_file':result_handle_file},context)
    else:
        form = UploadFileForm()
    return render_to_response('drivingtest/upload_excel_file.html', {'form': form},context)
@login_required
def upload_excel_file(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result_handle_file ="form is valid"
            choices =  form.cleaned_data['sheetchoice']
            is_available_file_tick =  form.cleaned_data['is_available_file']
            if not is_available_file_tick: # Neu khong tick vao cai o chon file co san
                if 'file' in request.FILES:
                    fcontain = request.FILES['file'].read()
                    workbook = xlrd.open_workbook(file_contents=fcontain)
                    import_database_4_cai_new(choices,workbook = workbook,is_available_file=False)
                else: # but not file upload so render invalid
                    result_handle_file = 'Invalid choices, please select file or tick into "is_available_file"'
                    return render_to_response('drivingtest/import_db_from_excel.html', {'form': form,'result_handle_file':result_handle_file},context)
            else:
                import_database_4_cai_new(choices,workbook = None,is_available_file=is_available_file_tick)
            return render_to_response('drivingtest/import_db_from_excel.html', {'form': form,'result_handle_file':result_handle_file},context)
    else:
        #form = UploadFileForm()
        return render_to_response('drivingtest/import_db_from_excel.html', {},context)
def download_script1(request):
    id_3g = request.GET['id_3g']
    print 'id_3g',id_3g
    #print settings.MEDIA_ROOT
    filename = settings.MEDIA_ROOT + '/for_user_download_folder/KG5733_IUB_W12_3.mo' # Select your file here.                                
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=test.txt'

    response['Content-Length'] = os.path.getsize(filename)
    return response
import tempfile, zipfile

def download_script(request,file_names=None):
    """                                                                         
    Create a ZIP file on disk and transmit it in chunks of 8KB,                 
    without loading the whole file into memory. A similar approach can          
    be used for large dynamic PDF files.                                        
    """
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    file_names = ['KG5733_IUB_W12_3.mo','KG5733_OAM_W12_1.xml','KG5733_SE-2carriers_2.xml']
    for file_name in  file_names:
        script_file = settings.MEDIA_ROOT + '/for_user_download_folder/' + file_name # Select your file here.                              
        archive.write(script_file, file_name)
    archive.close()
    
    
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=test.zip'
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response


#https://docs.djangoproject.com/en/1.8/howto/outputting-csv/




#############################################################################








 

def index(request):
    forum_choice_form = ForumChoiceForm()
    # [('1','a'),('2','b')] [(x['url'],x['url']) for x in danhsachforum]
    print 'danh sach',[(x['url'],x['url']) for x in danhsachforum]
    forum_choice_form.fields['forumchoice'].choices = [(x['url'],x['url']) for x in danhsachforum]
    #return render(request, 'drivingtest/index.html', context_dict)
    leech_entry_lists = Ulnew.objects.all().order_by('-id')
    table = PersonTable(Ulnew.objects.all())
    RequestConfig(request, paginate={"per_page": 40}).configure(table)

    #return render(request, 'drivingtest/people.html', {'table': table})
    
    siteobj = ForumTable.objects.get(url = 'http://amaderforum.com/')
    shaanigsite = ForumTable.objects.get(url = 'http://www.shaanig.com/')
    for entry in leech_entry_lists:
        try:
                #posted_ama = Ulnew.objects.get(forumback=siteobj,postLog__Ulnew=entry)
                posted_ama= PostLog.objects.get(forum=siteobj, Ulnew=entry)
                entry.is_post_amaforum = posted_ama.pested_link
               
                #entry.is_post_amaforum = 'yes'
        except:
            entry.is_post_amaforum = 'N'
        try:
                #posted_ama = Ulnew.objects.get(forumback=siteobj,postLog__Ulnew=entry)
          
                posted_shaanigsite= PostLog.objects.get(forum=shaanigsite, Ulnew=entry)
                entry.is_post_shaanig = posted_shaanigsite.pested_link
                #entry.is_post_amaforum = 'yes'
        except:
            entry.is_post_shaanig = 'N'
    
    leechsites = LeechSite.objects.all()
    for leechsite in leechsites:
        leechsite.leech_categories=[]
        
        one_cate = leechsite.music
        if one_cate:
            leechsite.leech_categories.append(one_cate)
        one_cate = leechsite.tv_show 
        if one_cate:
            leechsite.leech_categories.append(one_cate)
        one_cate = leechsite.anime
        if one_cate:
            leechsite.leech_categories.append(one_cate)
        one_cate = leechsite.movie
        if one_cate:
            leechsite.leech_categories.append(one_cate)
    
    '''
    
    leechsite.HDmovie
    leechsite.software
    leechsite.game
    leechsite.anime
    leechsite.mobile
    leechsite.ebook
    '''
    #context_dict = {'forum_choice_form':forum_choice_form,'leech_entry_lists':leech_entry_lists,'leechsites':leechsites}
    context_dict = {'forum_choice_form':forum_choice_form,'leech_entry_lists':leech_entry_lists,'table': table,'leechsites':leechsites}

    return render_to_response("drivingtest/index.html",
                          context_dict, context_instance=RequestContext(request))

def select_forum(request):
    try:
        forum_choice_form = ForumChoiceForm(request.POST)
        if forum_choice_form.is_valid():
            print 'valid'
        else:
            print 'notvalid'
        print 'type(request.POST)',type(request.POST)
        print 'request.POST',request.POST
        notification =  u'{0}'.format(request.body) + '\n' + u'{0}'.format(request.POST['forumchoice'])
        btn = request.POST['btn']
        #return render(request, 'drivingtest/notice.html', {'notification':notification})
        site_will_posts = request.POST.getlist('forumchoice')
        print 'site_will_post',site_will_posts
        #print 'type of site_will_post', type(site_will_post)
        post_sitedict_list = []
        #stuff = map(lambda w: bbcode.find(w) , prefix_links)
        for site_will_post in site_will_posts:
            for site in danhsachforum:
                    if site['url'] == site_will_post:
                        post_sitedict_list.append(site)
        print >>sys.stderr ,'you choice',post_sitedict_list
        print 'so luong hien dang ton tai',len(postdict)
        if btn == 'start':
        
            if 'choiceallentry' in request.POST:
                print 'ban chon het topic'
                entry_id_lists = ['all']
            else:
                entry_id_lists = request.POST.getlist('selection')
            print 'entry_id_lists',entry_id_lists
            
            
            for dict_site in post_sitedict_list:
                try:
                    if postdict[dict_site['url']].is_alive():
                        print 'luong dang chay bam stop cai da'
                        return render(request, 'drivingtest/notice.html', {'notification':'luong dan chay bam stop cai da'})
                    else:
                        pass
                except:
                    print 'New program...let post '
                postdict[dict_site['url']] = PostObject(dict_site,entry_id_lists)
                postdict[dict_site['url']].login_flag = 1
                postdict[dict_site['url']].start()
                print 'chuan bi vao ct post o view'
        elif btn == 'stop':
            print 'dang stop...o view'
            for dict_site in post_sitedict_list:
                print 'postdict',postdict
                print 'dict_site',dict_site['url']
                print 'luong dang ton tai',postdict[dict_site['url']]
                print 'type of postdict truoc stop ',type(postdict)
                print 'type luong dang ton tai',type (postdict[dict_site['url']])
                try:
                    #if postdict[dict_site['url']].is_alive():
                    postdict[dict_site['url']].stop  = True
                    print 'type of postdict sau stop ',type(postdict)
                    postdict[dict_site['url']].join()
                    print 'type of postdict sau join ',type(postdict)
                    notification = 'luong da stop xong, bat dau chay'
                    print 'luong da stop xong, bat dau chay'
                except Exception as e:
                    print 'luong chua ton tai' ,e
        return render(request, 'drivingtest/notice.html', {'notification':notification})
    except Exception as e:
        print type(e),e
        return render(request, 'drivingtest/notice.html', {'notification':"loi gi do"})
    
def leech(request):
    notification = u'{0}'.format(request.POST)
    print 'type of notification',type(notification)
    print notification
    cate_page = request.POST['cate-select']
    begin_page = int(request.POST['rangepagebegin'])
    end_page = int(request.POST['rangepageend'])
    #notification = 'notification'
    leech_bai(cate_page, begin_page, end_page)
    return render(request, 'drivingtest/notice.html', {'notification':notification})
def importul(request):
    #notification = u'dang import ul'
    
    txt = get_link_from_db()
    import_ul_txt_to_myul(txt)
    log=thongbao.log 
    return render(request, 'drivingtest/notice.html', {'notification':thongbao.thongbao,'log':log})
def get_thongbao(request):
    #del abcdef
    try:
        notification = thongbao.thongbao
        log = thongbao.thongbao
        '''
        notification = newPostProcess.numer_entry_post + newPostProcess.thongbao
        log = newPostProcess.postlog
        '''
    except Exception as e:
        print e
        notification = thongbao.thongbao
    #notification = 'da xoa'
    return render(request, 'drivingtest/notice.html', {'notification':notification,'log':log})
def stop_post(request):
    #del abcdef
    
    site_will_post = request.POST['forumchoice']
    print 'site_will_stop',site_will_post
    print 'type of site_will_post', type(site_will_post)
    for site in danhsachforum:
        if site['url'] == site_will_post:
            dict_site = site
    print >>sys.stderr ,'you choice',dict_site
    print 'so luong hien dang ton tai',len(postdict)
    try:
        exit_thread = postdict[dict_site['url']]
        if exit_thread.is_alive():
            postdict[dict_site['url']].stop()
            postdict[dict_site['url']].join()
            notification = 'luong da stop xong, bat dau chay'
            print 'luong da stop xong, bat dau chay'
    except Exception as e:
        print 'luong chua ton tai' ,e
    return render(request, 'drivingtest/notice.html', {'notification':notification})
def edit_entry(request,entry_id):
    entry = Ulnew.objects.get(id = entry_id)
    entryformsave = UlnewForm(request.POST,instance = entry)
    entryformsave.save()
    if entryformsave.is_valid():
        print 'valid'
    else:
        print entryformsave.errors
    notification = 'ban dang sua entry'
    #notification =  u'{0}'.format(request.body)
    #notification = 'da xoa'
    return render(request, 'drivingtest/notice.html', {'notification':notification})
import bbcode

def get_description(request):
    parser = bbcode.Parser()
    parser.add_simple_formatter('img', '<img  src="%(value)s">',replace_links=False)
    if request.method == 'GET':
        
        entry_id = request.GET['entry_id']
    entry = Ulnew.objects.get(id = entry_id)
    dllink=''
    if  entry.rg:
        dllink = dllink + '\n[code]' + entry.rg + '[/code]\n'
    if  entry.ul:
        dllink = dllink + '\n[code]' + entry.ul + '[/code]\n'    
    content = entry.description  + dllink
    html = parser.format(content)
    entry_form = UlnewForm(instance = entry) 
    #html = bbcode.render_html(content)
    notification =  html
    #notification = 'da xoa'
    return render(request, 'drivingtest/load_entry.html', {'notification':notification,'form':entry_form,'entry_id':entry_id})









   
