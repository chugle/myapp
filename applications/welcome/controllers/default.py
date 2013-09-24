# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from gluon.tools import Crud

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """

    message=''
    return dict(message=message)

@auth.requires_login()
def course_list():
    import datetime
    now=datetime.date.today()
    y=now.year
    m=now.month
    jie = auth.user.jie   
    if int(m) in range(2,8):
        xueqi=2
        nianji=int(y)-2000-int(jie)+3

        xuenian=str(int(y)-1-2000)
    else:
        xueqi=1
        nianji=int(y)-2000-int(jie)+4
        xuenian=str(int(y)-2000)
    rows=db((db.keshi.xuenian==xuenian)&(db.keshi.xueqi==xueqi)&(db.keshi.nianji==nianji)&(db.keshi.showed==True)).select(
                                                                                                  left=db.keshi.on(db.keshi.kecheng==db.course.id))
    return dict(rows=rows)

@auth.requires_login()
def study():

    keshi_id=request.args[0]
    record=db.keshi[keshi_id]
    kecheng_id=record.kecheng
    haszuoye=record.haszuoye
    kecheng=db.course[kecheng_id]
    title=kecheng.title
    neirong=kecheng.neirong
    kejian=kecheng.kejian
    
    
    rows=db(db.course.id==kecheng_id).select(db.course.kejian)
    lianxi_url=A('练习',_href=URL('lianxi/%s'%keshi_id))
    if haszuoye:
        zuoye_url=A('作业',_href=URL('zuoye/%s'%keshi_id))
    else:
        zuoye_url=BR()
    defen_url=A('得分',_href=URL('defen/%s'%keshi_id))
    return dict(keshi_id=keshi_id,lianxi_url=lianxi_url,zuoye_url=zuoye_url,defen_url=defen_url,
               title=title,neirong=neirong,kejian=kejian,rows=rows)

@auth.requires_login()  
def defen():
    zuozhe=auth.user_id
    keshi_id=request.args[0]
    rows=db((db.zuoti.zuozhe==zuozhe)&(db.lianxi.keshi==keshi_id)).select(    
                                                                       db.timu.wenti,
                                                                       db.zuoti.zuoda,
                                                                       db.timu.daan,orderby=db.lianxi.bianhao,
                                                                       join=db.lianxi.on(
                                                                                         (db.lianxi.timu==db.timu.id)&
                                                                                         (db.zuoti.lianxi==db.lianxi.id)),
																		
                                                                       )
    
    n=0;   right=0; cj=0
    for row in rows:
        n=n+1
        if row.zuoti.zuoda==row.timu.daan:
            right=right+1
    if n>0:
        cj=int(right*100/n)
    if not db.defen((db.defen.keshi==keshi_id)&(db.defen.xuesheng==zuozhe)):
        db.defen.insert(keshi=keshi_id,xuesheng=auth.user_id,chengji=cj)
    return dict(rows=rows,cj=cj,keshi_id=keshi_id)

@auth.requires_login()
def zuoye():
    zuozhe=auth.user_id
    keshi_id=request.args[0]
    crud=Crud(db)
    if db.zuoye((db.zuoye.zuozhe==zuozhe)&(db.zuoye.keshi==keshi_id)):
        db.zuoye.defen.writable=False
        zuoye_id=db.zuoye((db.zuoye.zuozhe==zuozhe)&(db.zuoye.keshi==keshi_id)).id
        form=crud.update(db.zuoye,zuoye_id,deletable=False,next=request.url)
        db.zuoye.defen.writable=True
    else:
        db.zuoye.zuozhe.default=zuozhe
        db.zuoye.keshi.default=keshi_id
        db.zuoye.defen.writable=False
        form=crud.create(db.zuoye,next=request.url)
      #  db.zuoye.zuozhe.default=None
        db.zuoye.keshi.default=None
        db.zuoye.defen.writable=True
    return dict(form=form)
    
@auth.requires_login()
def lianxi():
    zuozhe=auth.user_id
    keshi_id=request.args[0]
    crud=Crud(db)
    lianxi=db(db.lianxi.keshi==keshi_id).select(orderby=db.lianxi.bianhao)
    values=None
 
    form=FORM('练习:',
                  keepvalues=True)
    form.append(BR())
    for l in lianxi:      
        form.append(XML(db.timu(l.timu).wenti))
        form.append(INPUT(_name=l.id))
        form.append(BR())
    form.append(INPUT(_type='submit',_value='提交'))
    if form.process().accepted:
        for (lx,zd) in form.vars.items():
            db.zuoti.update_or_insert((db.zuoti.lianxi==lx)&(db.zuoti.zuozhe==zuozhe),
                                      lianxi=lx,zuozhe=zuozhe,zuoda=zd)
        redirect(URL('study',args=keshi_id))
    return dict(form=form)
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    response.headers['Pragma']="private"
    response.headers['Cache-Control']="private, must-revalidate"

    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
