# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()
auth.settings.extra_fields['auth_user']= [
  Field('jie',label='届'),
  Field('banji',label='班级')
]
auth.define_tables()
db.auth_user.first_name.label='姓名'
db.auth_user.last_name.label='学号'
db.auth_user.first_name.requires=IS_NOT_EMPTY()
db.auth_user.last_name.requires=[IS_NOT_EMPTY(),IS_MATCH('^\d\d$',error_message='two number:like 11,02')]
db.auth_user.jie.requires=[IS_NOT_EMPTY(),IS_MATCH('^\d\d$',error_message='two number:like 11,02')]
db.auth_user.banji.requires=[IS_NOT_EMPTY(),IS_MATCH('^\d\d$',error_message='two number:like 11,02')]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled = ['profile']
## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
MAX_UPLOAD_FILESIZE=50000000
NETDISK_SIZE=100000000


import os
db.define_table('course',
                Field('title',requires=IS_NOT_EMPTY(),label='名称'),
                Field('nianji',requires=IS_IN_SET([1,2]),label='年级'),
                Field('xueqi',requires=IS_IN_SET([1,2]),label='学期'),
                Field('neirong','text',label='内容'),
                Field('kejian','upload',
                      uploadfolder=os.path.join(request.folder,'uploads/kejian'),
                      autodelete=True,label='课件'),
                format='%(nianji)s-%(xueqi)s:%(title)s')

db.define_table('keshi',
                Field('xuenian',requires=IS_MATCH('\d\d'),label='学年'),
                Field('xueqi',requires=IS_NOT_EMPTY(),label='学期'),
                Field('nianji',requires=IS_IN_SET([1,2]),label='年级'),
                Field('keshi',requires=IS_NOT_EMPTY(),label='课时'),
                Field('kecheng',db.course,label='课程'),
                Field('haszuoye','boolean',default=True),
                Field('showed','boolean'),
                format='%(xuenian)s-%(xueqi)s.%(nianji)s:%(keshi)s')

db.define_table('timu',
                Field('course',db.course,label='课程'),
                Field('wenti',label='问题'),
                Field('daan',label='答案'),
                format='%(course)s_%(wenti)s')

db.define_table('lianxi',
                Field('keshi',db.keshi,label='课时'),
                Field('bianhao','integer',label='编号'),
                Field('timu',db.timu,label='题目'),
                )

db.define_table('zuoti',
                Field('lianxi',db.lianxi,label='练习'),
                Field('zuozhe',db.auth_user,label='作者'),
                Field('zuoda','text',label='答题'),
                Field('defen'),label='得分')

db.define_table('zuoye',
                Field('keshi',db.keshi,writable=False,widget=SQLFORM.widgets.string.widget,label='课时'),
                Field('zuozhe',db.auth_user,writable=False,widget=SQLFORM.widgets.string.widget,label='作者'),
                Field('wenjian','upload',autodelete=True,requires=IS_LENGTH(maxsize=MAX_UPLOAD_FILESIZE),label='文件'),
                Field('defen',writable=True,label='得分',requires=IS_IN_SET(['a','b','c','d','e'])))

db.define_table('wangpan',
                Field('yonghu',db.auth_user,readable=False,writable=False),
                Field('daxiao','integer'),
                Field('leixin'),
                Field('wenjian','upload',autodelete=True,requires=IS_LENGTH(maxsize=MAX_UPLOAD_FILESIZE)))

db.define_table('defen',Field('keshi',db.keshi,label='课时'),
                Field('xuesheng',db.auth_user,label='学生'),
                Field('chengji'),label='成绩')