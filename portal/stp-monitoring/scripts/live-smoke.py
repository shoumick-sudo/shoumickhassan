"""Synthetic end-to-end check of the deployed portal. Never logs credentials."""
import json,uuid,secrets,urllib.request,urllib.error,http.cookiejar
BASE='https://stp-monitoring-portal.onrender.com'
jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(url,method='GET',data=None,token=None):
 headers={'Content-Type':'application/json','Origin':BASE}
 if token:headers['Authorization']='Bearer '+token
 r=urllib.request.Request(url,method=method,headers=headers,data=None if data is None else json.dumps(data).encode())
 try:
  with opener.open(r,timeout=45) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
showcase='00000000-0000-4000-8000-000000000001'
assert req(BASE+'/health')[1]['ok']
assert req(BASE+'/api/workspaces')[0]==401
assert req(BASE+f'/api/workspaces/{showcase}/actions','POST',{})[0]==403
cfg=req(BASE+'/api/config')[1];auth=cfg['authURL']
status,d=req(auth+'/sign-up/email','POST',{'email':'live-qa-'+str(uuid.uuid4())+'@stp-portal.invalid','name':'Live deployment QA · synthetic','password':secrets.token_urlsafe(24)})
assert status==200,('signup',status)
status,d=req(auth+'/token');assert status==200 and d.get('token'),('token',status);token=d['token']
def api(path,method='GET',data=None):return req(BASE+'/api'+path,method,data,token)
status,w=api('/workspaces','POST',{'name':'Live smoke QA · synthetic'});assert status==201,('workspace',status,w.get('error'));path='/workspaces/'+w['id']
scores={k:3 for k in ['infrastructure','equipment','trainers','records','assessment_readiness']}
status,s=api(path+'/reports/MON-0193/submissions','POST',{'scores':scores});assert status==201
assert api(path+'/data')[1]['rows'][192]['versions'][0]['id']==s['id']
assert api(path+'/submissions/'+s['id']+'/review','POST',{'decision':'approved','note':'Live deployment QA: checked all five synthetic criteria'})[0]==200
assert api(path+'/data')[1]['rows'][192]['score']==75
item={'provider_id':'DEMO-STP-001','title':'Live deployment synthetic correction','owner':'QA fictional owner','due_date':'2026-10-30','status':'closed','verification':'pending','evidence':''}
assert api(path+'/actions','POST',item)[0]==400
item.update(status='open');status,a=api(path+'/actions','POST',item);assert status==201
item.update(status='closed',verification='verified',evidence='SIMULATED: live deployment evidence reference',revision=1)
assert api(path+'/actions/'+a['id'],'PATCH',item)[0]==200
reloaded=api(path+'/data')[1];assert next(x for x in reloaded['actions'] if x['id']==a['id'])['status']=='closed'
assert any(x['event']=='submission_approved' for x in reloaded['audit'])
req(auth+'/sign-out','POST',{})
print(json.dumps({'result':'PASS','checks':['health','unauthenticated denial','immutable public showcase','real managed signup and JWT','private workspace','saved draft and reload','review and score','blocked incomplete closure','verified saved closure','audit persistence'],'workspace':w['id'],'action':a['id']}))
