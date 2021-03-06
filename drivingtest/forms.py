# -*- coding: utf-8 -*-
'print in form 4'
from django import forms
from drivingtest.models import Table3g, Ulnew,\
    Mll, Command3g, SearchHistory, CommentForMLL, Doitac, TrangThaiCuaTram, UserProfile, Duan, SpecificProblem, FaultLibrary,ThietBi, EditHistory
from crispy_forms.layout import Submit, Field
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.html import   strip_tags
from django.forms.fields import DateTimeField, FileField
from datetime import datetime
from django.core.exceptions import ValidationError
from toold4 import luu_doi_tac_toold4
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from crispy_forms.bootstrap import AppendedText, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,HTML, Div
from crispy_forms.bootstrap import TabHolder, Tab
from django.template.context import Context, RequestContext
from django.template.loader import get_template
import re
from django_tables2_reports.tables import TableReport
from django.template.base import Template
from exceptions import IndexError
from django_tables2_reports.config import RequestConfigReport
from django.http.response import HttpResponse, StreamingHttpResponse
import xlwt
import collections
from django_tables2_reports.csv_to_xls.xlwt_converter import write_row
import csv

D4_DATETIME_FORMAT = '%H:%M %d/%m/%Y'
TABLE_DATETIME_FORMAT = "H:i d/m/Y "
######CONSTANT
CHOICES=[('Excel_3G','Ericsson 3G'),('Excel_to_2g','Database 2G'),\
         ('Excel_to_2g_config_SRAN','2G SRAN HCM Config'),\
         ('Excel_to_3g_location','3G Site Location'),('ALL','ALL'),\
         ('Excel_ALU','Excel_ALU'),('Excel_NSM','Excel_NSM'),
         ]
NTP_Field = ['ntpServerIpAddressPrimary','ntpServerIpAddress1','ntpServerIpAddress1','ntpServerIpAddress2']       
W_VErsion = [('W12','W12'),('W11','W11')]
#Function for omckv2
def doitac_showing (dt,is_show_donvi = False,prefix =''):
    if  dt:
        donvi = ('-' + dt.Don_vi ) if (dt.Don_vi and is_show_donvi) else ''
        sdt = ('-' + dt.So_dien_thoai) if dt.So_dien_thoai else ''
        htmlrender =  '<a href="#" class="edit-contact" id="%s">'%dt.id + prefix + dt.Full_name + donvi + sdt +'</a>'
        return mark_safe(htmlrender)
    else:
        return ''
#FIELD For OMCKV2
class DateTimeFieldWithBlankImplyNow(DateTimeField):
    def to_python(self, value):
        if value in self.empty_values:
            return datetime.now()
        else:
            rs = super(DateTimeFieldWithBlankImplyNow,self).to_python(value)
            return rs
class ChoiceFieldConvertBlank(forms.ModelChoiceField):
    def to_python(self, value):
        if value in self.empty_values:
            value = self.queryset.get(id = 1)
            return value
        else:
            value = super(ChoiceFieldConvertBlank,self).to_python(value)
        return value
'''     
class ChoiceFielddButWidgetTextInput(forms.CharField):
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }
    def __init__(self,queryset=None,to_python_if_leave_blank=None, *args, **kwargs):
        super(ChoiceFielddButWidgetTextInput,self).__init__( *args, **kwargs)
        self.queryset = queryset
        self.to_python_if_leave_blank = to_python_if_leave_blank
    def to_python(self, value):
        if value in self.empty_values:
            if self.to_python_if_leave_blank:
                value = self.queryset.get(**self.to_python_if_leave_blank)
                return value
            else:
                return None
        try:
            value = self.queryset.get(**{'Name': value})
            return value
        except (ValueError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice']%{'value':value})
    def prepare_value(self, value): # co chuc nang value cua widget
        if isinstance(value, int):
            value = self.queryset.get(id=value).Name
            return value
        else:
            return value

class TrangThaiField(ChoiceFielddButWidgetTextInput):
    default_error_messages = {
        'invalid_choice': _('khong co trang thai nao la "%(value)s" ca'),
        #'Select a valid choice. %(value)s is not one of the available choices.'
    }
'''
   

class DoiTacField(forms.CharField):
    def __init__(self,queryset=None, *args, **kwargs):
        super(DoiTacField,self).__init__( *args, **kwargs)
        self.queryset = queryset
    def prepare_value(self, value):# value for render as_widget
        if not value:
            return ''
        if isinstance(value, int):
            pass
        else:
            return value
        doi_tac = self.queryset.get(id=value)
        if doi_tac:
            doi_tac_return_to_form = doi_tac.Full_name  + (('-' + doi_tac.Don_vi ) if doi_tac.Don_vi else '') + (('-' + doi_tac.So_dien_thoai ) if doi_tac.So_dien_thoai else '')
        else:
            doi_tac_return_to_form=''
        return doi_tac_return_to_form
    def to_python(self, doi_tac_inputext):
        doi_tac_obj = luu_doi_tac_toold4(self.queryset,doi_tac_inputext)
        return doi_tac_obj
        #raise ValidationError(self.error_messages['invalid_choiced4'], code='invalid_choice')
class DoiTacFieldForFilterMLL(DoiTacField):
    def to_python(self, doi_tac_inputext):
        doi_tac_obj = luu_doi_tac_toold4(self.queryset,doi_tac_inputext,is_save_doitac_if_not_exit=False)
        return doi_tac_obj
#FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFOOOOOOOOOOOOOOOOOOORMFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF       


class UploadFileForm(forms.Form):
    sheetchoice = forms.MultipleChoiceField(choices=CHOICES,widget=forms.CheckboxSelectMultiple,label="Which Sheet you want import?",required=False)
    file = forms.FileField(label="Chon file database_3g excel",required=False)
    is_available_file = forms.BooleanField (required=False,label = "if available in media/document folder")

class BaseTableForManager(TableReport):
    is_report_download = True
    edit_comlumn = tables.Column(accessor="pk", orderable=False,)    
    def render_edit_comlumn(self,value):
        return mark_safe('<div><button class="btn  btn-default edit-entry-btn-on-table" id= "%s" type="button">Edit</button></div></br>'%value)
    def as_row_generator(self):
        csv_header = [column.header for column in self.columns]
        yield csv_header
        for row in self.rows:
            csv_row = []
            for column, cell in row.items():
                if isinstance(cell, basestring):
                    # if cell is not a string strip_tags(cell) get an
                    # error in django 1.6
                    cell = strip_tags(cell)
                else:
                    cell = unicode(cell)
                csv_row.append(cell)
            yield csv_row
    def as_xls_d4_in_form_py_csv(self, request):
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in self.as_row_generator()),
                                         content_type="text/csv")
        file_name = self.Meta.model.__name__
        response['Content-Disposition'] = 'attachment; filename="Table_%s.csv"'%file_name
        return response
    def as_xls_d4_in_form_py_xls(self,request):
        response = HttpResponse()
        file_name = self.Meta.model.__name__
        response['Content-Disposition'] = 'attachment; filename="Table_%s.xls"'%file_name
        # Styles used in the spreadsheet.  Headings are bold.
        header_font = xlwt.Font()
        header_font.bold = True
        header_style = xlwt.XFStyle()
        header_style.font = header_font
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')
        # Cell width information kept for every column, indexed by column number.
        cell_widths = collections.defaultdict(lambda: 0)
        csv_header = [column.header for column in self.columns if column.header!='Edit Comlumn']
        write_row(ws, 0, csv_header, cell_widths, style=header_style, encoding='utf-8')
        for lno,row in enumerate(self.rows):
            csv_row = []
            for column, cell in row.items():
                if column.header=='Edit Comlumn':
                    continue
                if isinstance(cell, basestring):
                    # if cell is not a string strip_tags(cell) get an
                    # error in django 1.6
                    cell = strip_tags(cell)
                else:
                    cell = unicode(cell)
                csv_row.append(cell)

            write_row(ws, lno+ 1, csv_row, cell_widths, style=None, encoding='utf-8')
        # Roughly autosize output column widths based on maximum column size.
        for col, width in cell_widths.items():
            ws.col(col).width = width
        setattr(response, 'content', '')
        wb.save(response)
        return response
class BaseFormForManager(forms.ModelForm):
    design_common_button = True
    modal_prefix_title = "Detail"
    allow_edit_modal_form = False
    is_update_edit_history = False
    def __init__(self,*args, **kw):
        self.loai_form = kw.pop('form_table_template',None)
        self.is_loc = kw.pop('loc',False)
        is_allow_edit = kw.pop('is_allow_edit',False)
        self.request = kw.pop('request',None)
        self.instance_input = kw.get('instance',None)
        if self.is_update_edit_history:
            self.update_edit_history()
        super(BaseFormForManager, self).__init__(*args, **kw)
        self.helper = FormHelper(form=self)
        if self.design_common_button:
            if self.loai_form =='form on modal' and  self.allow_edit_modal_form or is_allow_edit:
                self.helper.add_input(Submit('add-new', 'ADD NEW',css_class="submit-btn"))
            elif self.loai_form =='form on modal' and not self.allow_edit_modal_form:
                pass
            else: #loai_form =='normal form template' or None
                self.helper.add_input(Submit('add-new', 'ADD NEW',css_class="submit-btn"))
                self.helper.add_input(Submit('cancel', 'Cancel',css_class="btn-danger cancel-btn"))
                self.helper.add_input(Submit('manager-filter', 'Lọc',css_class="btn-info loc-btn"))
        self.helper.form_id = 'model-manager'
    def update_edit_history(self):
        if self.instance_input:
            querysets = EditHistory.objects.filter(modal_name=self.Meta.model.__name__,edited_object_id = self.instance_input.id)
            table = EditHistoryTable(querysets)
            RequestConfigReport(self.request, paginate={"per_page": 10}).configure(table)
            t = Template('{% load render_table from django_tables2 %}{% render_table table "drivingtest/custom_table_template_mll.html" %}')
            c = RequestContext(self.request,{'table':table})
            self.htmltable = '<div id="same-ntp-table" class = "form-table-wrapper"><div class="table-manager">' + t.render(c)  + '</div></div>'
            self.htmltable = HTML(self.htmltable)
        else:
            print '##########self.Meta.model.__name__,',self.Meta.model.__name__,
            self.htmltable=HTML('cai nay dung de luu lai lich su edit')
    def update_action_and_button(self,action_url):
        self.helper.form_action = action_url
        c = re.compile('/(\w+)/$')
        entry_id = c.search(action_url).group(1)
        if self.helper.inputs:
            if entry_id=='new':
                try:
                    self.helper.inputs[0].value = "ADD NEW"
                    self.helper.inputs[0].field_classes = self.helper.inputs[0].field_classes.replace('btn-warning','btn-primary')
                except IndexError:
                    pass
                if self.loai_form =='form on modal':
                    self.modal_prefix_title="ADD"
                    self.modal_title_style = self.modal_add_title_style
            else:
                try:
                    self.helper.inputs[0].value = "EDIT"
                    self.helper.inputs[0].field_classes  = self.helper.inputs[0].field_classes.replace('btn-primary','btn-warning')
                except IndexError:
                    pass
                if self.loai_form =='form on modal':
                    self.modal_prefix_title="Detail"
                    self.modal_title_style = getattr(self,'modal_edit_title_style',None)
    def clean(self):
        if self.is_loc:
            self._validate_unique = False
        else:
            self._validate_unique = True
        return self.cleaned_data
    def _post_clean(self):
        if self.is_loc:
            pass
        else:
            super(BaseFormForManager,self)._post_clean()
    '''
    def _post_clean(self):
        print 'nhay vao valid post_clean'
        opts = self._meta
        # Update the model instance with self.cleaned_data.
        self.instance_input = construct_instance(self, self.instance_input, opts.fields, opts.exclude)

        exclude = self._get_validation_exclusions()

        # Foreign Keys being used to represent inline relationships
        # are excluded from basic field value validation. This is for two
        # reasons: firstly, the value may not be supplied (#12507; the
        # case of providing new values to the admin); secondly the
        # object being referred to may not yet fully exist (#12749).
        # However, these fields *must* be included in uniqueness checks,
        # so this can't be part of _get_validation_exclusions().
        for f_name, field in self.fields.items():
            if isinstance(field, InlineForeignKeyField):
                exclude.append(f_name)

        try:
            self.instance_input.full_clean(exclude=exclude,
                validate_unique=False)
        except ValidationError as e:
            #print '22e.error_dict',e.error_dict
            if self.is_loc:
                for fname,instance_ValidationError_lists in e.error_dict.items():
                    for instance_ValidationError in instance_ValidationError_lists:
                        if 'This field cannot be blank' in instance_ValidationError.message:
                            if len(instance_ValidationError_lists)==1:
                                del e.error_dict[fname]
                            else:
                                instance_ValidationError_lists.remove(instance_ValidationError)
            #print '**e',e
            self._update_errors(e)
            
        # Validate uniqueness if needed.
        if self._validate_unique:
            self.validate_unique()
    '''
    def _clean_fields(self):
        print '@@self.cleaned_data',self.cleaned_data
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                #print '^^^^e _clean_fields',e
                # moi them
                #print 'type of e.messages',type(e.messages)
                #for x in e.messages:
                    #print '111typeof x in e.messages',type(x)
                e_code = getattr(e,'code',None)
                if self.is_loc and e_code=='required':
                    self.cleaned_data[name] = value
                    continue
                print '**continue'
                #end moi them
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]
class Command3gForm(BaseFormForManager):

    def __init__(self, *args, **kwargs):
        super(Command3gForm, self).__init__(*args, **kwargs)
        self.helper.form_action='/omckv2/modelmanager/Command3gForm/new/'
        self.helper.layout = Layout(Div(Field('command'),css_class='col-sm-4'),Div(Field('ten_lenh'),css_class='col-sm-4'),Div(Field('mo_ta'),css_class='col-sm-4'))
        
    class Meta:
        model = Command3g
        widgets = {'command':forms.Textarea,'ten_lenh':forms.Textarea,'mo_ta':forms.Textarea}  
class DoitacForm(BaseFormForManager):
    allow_edit_modal_form = True
    class Meta:
        model = Doitac
        exclude = ('Full_name_khong_dau','First_name')
class ThietBiForm(BaseFormForManager):
    #phone_regex2 = RegexValidator(regex= r'\w{9,15}', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    #ghi_chu_cho_thiet_bi = forms.CharField(validators=[phone_regex2]) # validators should be a list
    class Meta:
        model = ThietBi
    
class TrangThaiCuaTramForm(BaseFormForManager):
    class Meta:
        model = TrangThaiCuaTram
class TrangThaiCuaTramTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/TrangThaiCuaTramForm/new/'
    class Meta:
        model = TrangThaiCuaTram
        attrs = {"class": "table table-bordered"}
class DuanForm(BaseFormForManager):
    readonly_fields = ('Name','duoc_tao_truoc')
    def __init__(self, *args, **kwargs):
        super(DuanForm, self).__init__(*args, **kwargs)
        self.fields['doi_tac_du_an'].help_text=u''
    def clean(self):
        cleaned_data = super(DuanForm,self).clean()
        if self.instance_input and self.instance_input.duoc_tao_truoc:
            for field in self.readonly_fields:
                origial_value  = getattr(self.instance_input, field)
                if  cleaned_data[field] != origial_value: 
                    msgs = [u"khong duoc thay doi field nay"]
                    self._errors[field] = self.error_class(msgs)
                    #if field in self.cleaned_data:
                        #del self.cleaned_data[field]
        return cleaned_data
    class Meta:
        model = Duan
        widgets = {'Mota':forms.Textarea()}
class FaultLibraryForm(BaseFormForManager):
    class Meta:
        model = FaultLibrary
class SpecificProblemForm(BaseFormForManager):
    allow_edit_modal_form=True
    class Meta:
        model = SpecificProblem
        exclude = ('mll',)
class  UserProfileForm(BaseFormForManager):  
    class Meta:
        model = UserProfile      
class  ModelManagerForm(forms.Form):  
    chon_loai_de_quan_ly = forms.ChoiceField(required=False,widget = forms.Select(attrs={"class":"manager-form-select"}),\
    choices=[('/omckv2/modelmanager/DoitacForm/new/','Doi Tac'),('/omckv2/modelmanager/ThietBiForm/new/','Thiet Bi'),\
             ('/omckv2/modelmanager/DuanForm/new/','Du an'),\
             ('/omckv2/modelmanager/FaultLibraryForm/new/','FaultLibraryForm'),\
             ('/omckv2/modelmanager/TrangThaiCuaTramForm/new/','TrangThaiCuaTram'),\
             ('/omckv2/modelmanager/SpecificProblemForm/new/','SpecificProblemForm'),\
             ('/omckv2/modelmanager/UserProfileForm/new/','UserProfileForm'),
             ])
    def __init__(self, *args, **kwargs):
        super(ModelManagerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(form=self)
        self.helper.form_tag = False

class Command3gTable(TableReport):
    jquery_url= '/omckv2/modelmanager/Command3gForm/new/'
    selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    edit_comlumn = tables.Column(accessor="pk", orderable=False)
    class Meta:
        model = Command3g
        sequence = ("selection",)
        attrs = {"class": "table cm-table table-bordered"}
    def render_edit_comlumn(self,value):
        return mark_safe('<div><button class="btn  btn-default edit-entry-btn-on-table" id= "%s" type="button">Edit</button></div></br>'%value)
        
class ThietBiTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/ThietBiForm/new/'
    class Meta:
        model = ThietBi
        attrs = {"class": "table table-bordered"}
class DoitacTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/DoitacForm/new/'
    class Meta:
        model = Doitac
        attrs = {"class": "table table-bordered"}
class DuanTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/DuanForm/new/'
    class Meta:
        model = Duan
        attrs = {"class": "table table-bordered"}
class FaultLibraryTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/FaultLibraryForm/new/'
    class Meta:
        model = FaultLibrary
        attrs = {"class": "table table-bordered"}
class SpecificProblemTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/SpecificProblemForm/new/'
    class Meta:
        model = SpecificProblem
        attrs = {"class": "table table-bordered"}


class UserProfileTable(BaseTableForManager):
    jquery_url= '/omckv2/modelmanager/UserProfileForm/new/'
    class Meta:
        model = UserProfile
        attrs = {"class": "table table-bordered"}    
       
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        error_messages={'username':{'required': _('vui long nhap o nay!!')},}
class UserProfileForm_re(forms.ModelForm):
    #phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_regex1 = RegexValidator(regex=r'^\+' , message="Phone number must bat dau bang dau +")
    phone_regex2 = RegexValidator(regex= r'\w{9,15}', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    so_dien_thoai = forms.CharField(validators=[phone_regex1,phone_regex2]) # validators should be a list
    class Meta:
        model = UserProfile
        fields = ('so_dien_thoai',)
        
        
#$$$$$$$$$$$$$$$$$$MAINFORM
class CommentForMLLForm(BaseFormForManager):
    verbose_form_name  = 'Comment'
    modal_edit_title_style = 'background-color:#ec971f' 
    modal_add_title_style = 'background-color:#337ab7'
    allow_edit_modal_form=True
    datetime= DateTimeFieldWithBlankImplyNow(input_formats =[D4_DATETIME_FORMAT], widget =forms.DateTimeInput(format=D4_DATETIME_FORMAT,attrs={'class': 'form-control'}),help_text="leave blank if now",required=False)
    doi_tac = DoiTacField(queryset=Doitac.objects.all(),label = "Đối Tác",widget=forms.TextInput(attrs={'class':'form-control autocomplete','style':'width:600px'}),required=False)
    is_delete = forms.BooleanField(required=False,label= "Xóa comment này")
    trang_thai = ChoiceFieldConvertBlank(queryset=TrangThaiCuaTram.objects.all(),required = False,label = u'Trạng thái')
    mll = forms.CharField(required=False,widget = forms.HiddenInput())
    #mll = forms.CharField(required=False)
    def __init__(self,*args, **kw):
        super(CommentForMLLForm, self).__init__(*args, **kw)
        self.fields['thao_tac_lien_quan'].help_text=u'có thể chọn nhiều thao tác'
        if 'instance' not in kw:
            self.fields.keyOrder = ['mll','trang_thai','doi_tac','thao_tac_lien_quan','comment','datetime', ]
            #self.helper.add_input(Submit('create-comment', u'Create Comment',css_class="btn btn-primary"))
        else:
            self.fields.keyOrder = ['mll','trang_thai', 'doi_tac','thao_tac_lien_quan','comment','datetime','is_delete',]
            #self.helper.add_input(Submit('create-comment', u'Edit',css_class="btn btn-warning"))
        #self.helper.form_id = 'add-comment-form-id'
        #self.helper.form_id = 'model-manager'
        #self.helper.form_action = '/omckv2/load_edit_comment/'
        self.helper.layout = Layout(
Div(
     Div(AppendedText('datetime','<span class="glyphicon glyphicon-calendar"></span>'),css_class='input-group date datetimepicker-comment')),\
    'mll',
    Field('trang_thai',css_class='comboboxd4'),
    'thao_tac_lien_quan',
    'comment',
    'doi_tac',
    )
    class Meta:
        model = CommentForMLL
        exclude = ('mll','thanh_vien',)
        widgets = {
            'comment': forms.Textarea(attrs={'autocomplete': 'off'}),
        }
        '''
        labels = {
                'comment':u'Noi dung comment'
                 }
                 '''
        error_messages={
                        'comment':{'required': _('Please enter your name')}
                        }
        help_texts = {'thao_tac_lien_quan':'','comment':'add some comments'} 

GENDER_CHOICES = (
    ('male', _('Men')),
    ('female', _('Women')),
)

class NTPform(forms.Form):
    ntpServerIpAddressPrimary= forms.CharField(required=False,initial = '10.213.227.98')
    ntpServerIpAddressSecondary= forms.CharField(required=False,initial = '10.213.227.98')
    ntpServerIpAddress1= forms.CharField(required=False,initial = '10.213.227.98')
    ntpServerIpAddress2= forms.CharField(required=False,initial = '10.213.227.98')
    
    
    #####                            #####
    #############            #############
                    #    #
                    #    #
                    # Mllform   #
                    #    #
class SubjectField(forms.CharField):
    def to_python(self,value):
        value = re.sub(',\s*$','',value)
        return super(SubjectField,self).to_python(value)

class MllForm(BaseFormForManager):
    subject = SubjectField(required=True)
    id =forms.CharField(required=False,widget=forms.HiddenInput(attrs={'hidden-input-name':'id-mll-entry'}))
    gio_mat= DateTimeFieldWithBlankImplyNow(input_formats = [D4_DATETIME_FORMAT],widget =forms.DateTimeInput(format=D4_DATETIME_FORMAT,attrs={'class': 'form-control'}),help_text=u"bỏ trống nếu là bây giờ",required=False)
    gio_mat_lon_hon= forms.DateTimeField(label =u'giờ mất sau thời điểm', input_formats = [D4_DATETIME_FORMAT],required=False,help_text=u"dùng để lọc lớn hơn")
    gio_tot= forms.DateTimeField(input_formats = [D4_DATETIME_FORMAT],widget =forms.DateTimeInput(format=D4_DATETIME_FORMAT,attrs={'class': 'form-control'}),required=False)
    datetime = DateTimeFieldWithBlankImplyNow(label = u'Giờ của trạng thái',input_formats = [D4_DATETIME_FORMAT],widget =forms.DateTimeInput(format=D4_DATETIME_FORMAT,attrs={'class': 'form-control'}),help_text=u"bỏ trống nếu là bây giờ",required=False)
    trang_thai = ChoiceFieldConvertBlank(queryset=TrangThaiCuaTram.objects.all(),required = False,label = u'Trạng thái')
    doi_tac = DoiTacField(queryset=Doitac.objects.all(),label = "Đối Tác",widget=forms.TextInput(attrs={'class':'form-control autocomplete'}),required=False)
    #thanh_vien = forms.ModelChoiceField(queryset=User.objects.all(),label = "Thanh Vien",required=False,widget = forms.Select(attrs={'disabled':'disabled'}))

    comment = forms.CharField(label = u'Comment:',widget=forms.Textarea(attrs={'class':'form-control autocomplete'}),required=False)
    specific_problem_m2m = forms.CharField(required=False,widget=forms.Textarea(attrs={'class':'form-control'}))
    is_update_edit_history = True
    def __init__(self, *args, **kwargs):
        super(MllForm, self).__init__(*args, **kwargs)
        self.helper.form_action='/omckv2/modelmanager/MllForm/new/'
        self.helper.layout = Layout(
TabHolder(
    Tab('Nhap Form MLL',\
    Div('id',
        Field('subject',css_class="autocomplete_search_tram"), \
        Field('nguyen_nhan',css_class= 'comboboxd4'),\
        Div(AppendedText('gio_mat','<span class="glyphicon glyphicon-calendar"></span>'),css_class='input-group date datetimepicker'),\
        Div(AppendedText('gio_tot','<span class="glyphicon glyphicon-calendar"></span>'),css_class='input-group date datetimepicker'), css_class= 'col-sm-4'),
    Div('site_name', Field( 'thiet_bi',css_class="mySelect2"),Field('du_an',css_class= 'comboboxd4'), Field( 'specific_problem_m2m',css_class= 'autocomplete') , css_class= 'col-sm-4'),
    Div(HTML('<h4>Comment đầu tiên</h4>'),Div(AppendedText('datetime','<span class="glyphicon glyphicon-calendar"></span>'),css_class='input-group date datetimepicker'),
        Field('trang_thai',css_class= 'comboboxd4'),Field('comment'),'doi_tac', css_class= 'col-sm-4 first-comment')
    ),
    
    
    Tab('Extra for filter', Div(Field('thanh_vien',css_class= 'comboboxd4'),'ca_truc',Div(AppendedText('gio_mat_lon_hon','<span class="glyphicon glyphicon-calendar"></span>'),css_class='input-group date datetimepicker'),'ung_cuu','giao_ca',css_class= 'col-sm-6')),             
    Tab('More Info','edit_reason','last_edit_member'),
       Tab('Hide form trực ca',)  
       ,
    Tab(
     'Edit History mllform',self.htmltable )
             
            ) #Tab end
)#Layout end
    class Meta:
        model = Mll
        exclude = ('gio_nhap','specific_problem','specific_problem_m2m','last_update_time')#,'thanh_vien'
        #widgets = {'thanh_vien':forms.Select(attrs={'disabled':'disabled'})}
        '''
        labels = {'comment':u'Nội dung comment'
                 }
        '''
#MllFormForMLLFilter la can thiet
class MllFormForMLLFilter(MllForm):
    doi_tac = DoiTacFieldForFilterMLL(queryset=Doitac.objects.all(),label = "Đối Tác",widget=forms.TextInput(attrs={'class':'form-control autocomplete'}),required=False)

class Table3g_NTPForm(BaseFormForManager):
    design_common_button = False
    #send_mail = forms.EmailField(max_length=30,required = False)
    allow_edit_modal_form = False
    def __init__(self, *args, **kwargs):
        super(Table3g_NTPForm, self).__init__(*args, **kwargs)
        
        self.helper.add_input(Submit('add-new', 'ADD NEW',css_class="edit-ntp submit-btn"))
        self.helper.add_input(Submit('download-script-first-argument', 'download-script',css_class="btn btn-primary link_to_download_scipt"))
        self.helper.add_input(Submit('first-argument', 'Update to db',css_class="edit-ntp submit-btn update_all_same_vlan_sites"))
        
    class Meta:
        model = Table3g
        fields = ['ntpServerIpAddressPrimary' ,'ntpServerIpAddressSecondary',\
                         'ntpServerIpAddress1','ntpServerIpAddress2']
        help_texts = {
            'ntpServerIpAddress2': _('Update will update all site have same NTPconfig'),
        }
from django_tables2 import RequestConfig    
class Table3gForm(BaseFormForManager):
    id =forms.CharField(required=False,widget=forms.HiddenInput())
    is_update_edit_history = True
    def __init__(self, *args, **kwargs):
        super(Table3gForm, self).__init__(*args, **kwargs)
        self.fields['du_an'].help_text=u'có thể chọn nhiều dự án'
        download_ahref = HTML("""<a href="/omckv2/modelmanager/Table3g_NTPForm/%s/" class="btn btn-default show-modal-form-link downloadscript">Download Script</a> """%self.instance_input.id) if (self.instance_input and self.instance_input.site_id_3g and 'ERI_3G' in self.instance_input.site_id_3g ) else None
        self.helper.form_action = '/omckv2/modelmanager/Table3gForm/new/'
        self.helper.layout = Layout(
        TabHolder(
            Tab(
                      'thong tin 3G',
                      Div('id','du_an_show','site_id_3g',  'site_name_1', 'site_name_2','BSC','site_ID_2G',css_class= 'col-sm-3'),
                      Div(  'ProjectE', 'Status', 'du_an', css_class= 'col-sm-3'),
                      Div( 'U900','License_60W_Power','Count_Province', 'Count_RNC','Ngay_Phat_Song_3G' , 'Port', css_class= 'col-sm-3'),
                      #Div(  'Cell_1_Site_remote', 'Cell_2_Site_remote', 'Cell_3_Site_remote','Cell_4_Site_remote', 'Cell_5_Site_remote','Cell_6_Site_remote','Cell_7_Site_remote', 'Cell_8_Site_remote', 'Cell_9_Site_remote', css_class= 'col-sm-3'),
                      Div('RNC' , 'Cabinet','UPE','GHI_CHU','BSC_2G', download_ahref , css_class= 'col-sm-3')
                     
            ),
            Tab('Truyen Dan 3G',
                Div('Trans','IUB_VLAN_ID', 'IUB_SUBNET_PREFIX', 'IUB_DEFAULT_ROUTER',css_class= 'col-sm-3'),
                Div( 'IUB_HOST_IP', 'MUB_VLAN_ID',  'MUB_SUBNET_PREFIX', 'MUB_DEFAULT_ROUTER', 'MUB_HOST_IP',css_class= 'col-sm-3')
            ),             
            Tab('thong tin 2G',
              Div('BSC_2G', 'LAC_2G','site_ID_2G','Cell_ID_2G','Ngay_Phat_Song_2G',css_class= 'col-sm-3'),
              Div('cau_hinh_2G', 'nha_san_xuat_2G', 'TG', 'TRX_DEF',css_class= 'col-sm-3')
            ),
           
            Tab(
                 'thong tin tram', 'Ma_Tram_DHTT','Nha_Tram','dia_chi_2G', 'dia_chi_3G',
            ),
            Tab('NTP','ntpServerIpAddressPrimary','ntpServerIpAddressSecondary',\
    'ntpServerIpAddress1',\
    'ntpServerIpAddress2',css_class= 'col-sm-3'),
            Tab(
                 'hide',HTML('Hide')
            ),
            Tab(
                 'Edit History',self.htmltable
            )
                
        )
    )
    
    def update_action_and_button(self,*args, **kwargs):
        super(Table3gForm, self).update_action_and_button(*args, **kwargs)
        self.update_edit_history()
        '''
        self.helper.form_action = action_url + '?lenthofhis=' +  self.lenthofhis
        c = re.compile('/(\w+)/$')
        entry_id = c.search(action_url).group(1)
        if self.helper.inputs:
            if entry_id=='new':
                try:
                    self.helper.inputs[0].value = "ADD NEW"
                    self.helper.inputs[0].field_classes = self.helper.inputs[0].field_classes.replace('btn-warning','btn-primary')
                except IndexError:
                    pass
                if self.loai_form =='form on modal':
                    self.modal_prefix_title="ADD"
                    self.modal_title_style = self.modal_add_title_style
            else:
                try:
                    self.helper.inputs[0].value = "EDIT"
                    self.helper.inputs[0].field_classes  = self.helper.inputs[0].field_classes.replace('btn-primary','btn-warning')
                except IndexError:
                    pass
                if self.loai_form =='form on modal':
                    self.modal_prefix_title="Detail"
                    self.modal_title_style = getattr(self,'modal_edit_title_style',None)
        '''
    class Meta:
        model = Table3g
        exclude=['License_60W_Power']
        help_texts = {'du_an':''}
######################################################################################################################################################
#                                                                                                                                                     #
#                                                                                                                                                     #
#                                                                                                                                                     #
#                                                                                                                                                     #
#                                                                                                                                                     #
######################################################################################################################################################
#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE#TABLE

#class SearchHistoryTable(TableReport):
import models
class EditHistoryTable(TableReport):
    is_report_download = False
    object_name = tables.Column(accessor="edited_object_id",verbose_name="object_name")
    jquery_url= '/omckv2/modelmanager/EditHistoryForm/new/'
    def render_object_name(self,record,value):
        Classofedithistory = eval('models.' + record.modal_name)
        instance = Classofedithistory.objects.get(id = value)
        return instance.__unicode__
        #return str(value)+ record.modal_name
    class Meta:
        model = EditHistory
        exclude = ('id','modal_name',)
        sequence = ('object_name',)
        attrs = {"class": "table-bordered"}
class SearchHistoryTable(TableReport):
    jquery_url= '/omckv2/modelmanager/SearchHistoryForm/new/'
    exclude = ('thanh_vien')
    edit_comlumn =  tables.Column(accessor="pk",)
    class Meta:
        model = SearchHistory
        attrs = {"class": "table history-table table-bordered","table-action":"/omckv2/edit_history_search/"}
    def render_edit_comlumn(self,value):
        return mark_safe('''<img src='media/images/pencil.png' class='btnEdit'/><img src='media/images/delete.png' class='btnDelete'/>''' )


class Table3gTable(BaseTableForManager):
    #selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    #jquery_url = '/omckv2/tram_table/'
    jquery_url= '/omckv2/modelmanager/Table3gForm/new/'
    #is_show_download_link = True
    class Meta:
        exclude = ("License_60W_Power", )
        model = Table3g
        sequence = ("site_id_3g","site_name_1","id",)
        attrs = {"class": "tram-table table-bordered"}
class Table3g_NTPTable(TableReport):
    #selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    #jquery_url = '/omckv2/tram_table/'
    jquery_url= '/omckv2/modelmanager/Table3g_NTPForm/new/'
    #is_show_download_link = True
    class Meta:
        fields=('site_id_3g','site_name_1','RNC','ntpServerIpAddressPrimary','ntpServerIpAddressSecondary','ntpServerIpAddress1','ntpServerIpAddress2')
        model = Table3g
        attrs = {"class": "same-ntp table-bordered"}

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
class MllTable(TableReport):
    is_report_download = True
    edit_comlumn = tables.Column(accessor="pk", orderable=False,)
    gio_tot = tables.DateTimeColumn(format=TABLE_DATETIME_FORMAT)
    #last_update_time = tables.DateTimeColumn(format="H:i d-m")
    doi_tac = tables.Column(accessor="doi_tac.Full_name",verbose_name="Doi tac")
    ca_truc = tables.Column(accessor="ca_truc.Name",verbose_name="Ca Trực")
    trang_thai = tables.Column(accessor="trang_thai.Name",verbose_name="Trang Thai")
    cac_buoc_xu_ly = tables.Column(accessor="pk")
    specific_problem = tables.Column(accessor="pk")
    #nguyen_nhan = tables.Column(accessor='nguyen_nhan.Name',verbose_name="nguyên nhân")
    jquery_url = '/omckv2/modelmanager/MllForm/new/'
    gio_mat = tables.DateTimeColumn(format=TABLE_DATETIME_FORMAT)
    class Meta:
        model = Mll
        attrs = {"class": "table tablemll table-bordered paleblue",'name':'MllTable'}#paleblue
        exclude=('gio_nhap','gio_bao_uc','last_update_time','doi_tac','last_edit_member','edit_reason')
        sequence = ('id','subject','site_name','thiet_bi','nguyen_nhan','du_an','ung_cuu','thanh_vien','ca_truc'\
                    ,'gio_mat','gio_tot','trang_thai','specific_problem','cac_buoc_xu_ly','edit_comlumn','giao_ca',)
    
    def as_row_generator(self):
        csv_header = [column.header for column in self.columns]
        yield csv_header
        for row in self.rows:
            csv_row = []
            for column, cell in row.items():
                if isinstance(cell, basestring):
                    # if cell is not a string strip_tags(cell) get an
                    # error in django 1.6
                    cell = strip_tags(cell)
                else:
                    cell = unicode(cell)
                csv_row.append(cell)
            yield csv_row
    def as_xls_d4_in_form_py_csv(self, request):
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in self.as_row_generator()),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        return response
    def as_xls_d4_in_form_py_xls(self,request):
        response = HttpResponse()
        file_name = self.Meta.model.__name__
        response['Content-Disposition'] = 'attachment; filename="Table_%s.xls"'%file_name
        # Styles used in the spreadsheet.  Headings are bold.
        header_font = xlwt.Font()
        header_font.bold = True
        header_style = xlwt.XFStyle()
        header_style.font = header_font
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')
        # Cell width information kept for every column, indexed by column number.
        cell_widths = collections.defaultdict(lambda: 0)
        csv_header = [column.header for column in self.columns if column.header!='Edit Comlumn']
        write_row(ws, 0, csv_header, cell_widths, style=header_style, encoding='utf-8')
        for lno,row in enumerate(self.rows):
            csv_row = []
            for column, cell in row.items():
                if column.header=='Edit Comlumn':
                    continue
                if isinstance(cell, basestring):
                    # if cell is not a string strip_tags(cell) get an
                    # error in django 1.6
                    cell = strip_tags(cell)
                else:
                    cell = unicode(cell)
                csv_row.append(cell)

            write_row(ws, lno+ 1, csv_row, cell_widths, style=None, encoding='utf-8')
        # Roughly autosize output column widths based on maximum column size.
        '''
        for col, width in cell_widths.items():
            ws.col(col).width = width
        '''
        setattr(response, 'content', '')
        wb.save(response)
        return response
    def render_specific_problem(self,value):
        mll = Mll.objects.get(id=value)
        sp_all =  mll.specific_problems.all()
        if not sp_all:
            return ''
        result = '<ul class="non-bullet-ul">'
        for x in sp_all:
            result = result + '<li>' + ( '<a  href="/omckv2/modelmanager/FaultLibraryForm/%s/" class="green-color-text show-modal-form-link">'%x.fault.id + ((x.fault.Name  + '</a>**' )) if x.fault else '')\
              + ( ('<a href="/omckv2/modelmanager/SpecificProblemForm/%s/" class="show-modal-form-link">'%x.id + x.object_name + '</a>') if x.object_name else '') + '</li>'
        result +='</ul>'
        result = mark_safe(result)
        return result
   
    def render_thanh_vien(self,value):
        return mark_safe('<a href="/omckv2/modelmanager/UserProfileForm/%s/" class="show-modal-form-link">%s</a>'%(User.objects.get(username=value).get_profile().id,value))
    def render_thiet_bi(self,value):
        tb_instance = ThietBi.objects.get(Name = value)
        return mark_safe('<a href="/omckv2/modelmanager/ThietBiForm/%s/" class="show-modal-form-link">%s</a>'%(tb_instance.id,value))
    def render_du_an(self,value):
        duan_instance = Duan.objects.get(Name = value)
        return mark_safe('<a href="/omckv2/modelmanager/DuanForm/%s/" class="show-modal-form-link">%s</a>'%(duan_instance.id,value))
    def render_trang_thai(self,value):
        if value ==u"Báo ứng cứu":
            value = u'<span class="bao-ung-cuu">{0}</span>'.format(value)
        return mark_safe(value)
    def render_doi_tac(self,value,record):
        mll = Mll.objects.get(id=record.id)
        dt = mll.doi_tac
        return doitac_showing (dt,is_show_donvi=True)
    def render_cac_buoc_xu_ly(self,value):
        mll = Mll.objects.get(id=value)
        #cms = '<ul class="comment-ul">' + '<li>' + (timezone.localtime(mll.gio_mat)).strftime(D4_DATETIME_FORMAT)+ ' ' + mll.cac_buoc_xu_ly + '</li>'
        querysetcm = mll.comments.all().order_by("id")

        t = get_template('drivingtest/comment_in_mll_table_show.html')
        c = Context({ 'querysetcm': querysetcm })
        #rendered = t.render(c)
        return mark_safe(t.render(c))
        
    def render_edit_comlumn(self,value):
        return mark_safe('''
        <div><button class="btn  btn-default edit-entry-btn-on-table" id= "%s" type="button">Edit</button></div></br>
        <div class="dropdown ">
  <button class="btn btn-primary d4btn dropdown-toggle dropdown-class" type="button" id="dropdownMenu1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
    Function<span class="caret"></span>
  </button>
  <ul class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenu1">
    <li class="delete"><a href="#">Delele </a></li>
    <li><a href="#">Nhắn tin ứng cứu</a></li>
    <li id="add-comment" hanhdong="add-comment"><a href="/omckv2/modelmanager/CommentForMLLForm/new/" class="show-modal-form-link add-comment">Add Comment</a></li>
  </ul>
</div>''' %value)
        


            
            








#END TABLE###########END TABLE####################END TABLE#############END TABLE####END TABLE########END TABLE#######END TABLE#####
#UL
        
        









#TRANGPHUKIEN------------------------------------------







#ULLLLLLL---------------------------

class ForumChoiceForm(forms.Form):
    forumchoice = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,label="Xin chon forum")
class UlnewForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    description= forms.CharField(widget=forms.Textarea(attrs={'class': 'special'}))
    class Meta:
        model = Ulnew
        
#Table for UL
#PersonTable(tables.Table)
class PersonTable(TableReport):
    selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    description = tables.Column(verbose_name="Mo ta")
    is_posted_shaanig = tables.Column(empty_values=())
    title = tables.Column()
    def render_is_posted_shaanig(self):
        return 'hk'
    def render_description(self,value):
        return value[:10]
    class Meta:
        model = Ulnew
        attrs = {"class": "paleblue"}
        sequence = ("selection", "date")
        
        
               
