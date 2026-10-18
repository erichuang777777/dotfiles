import json,pathlib,subprocess,threading,time,urllib.request,urllib.error,os,importlib.util
from tokenizers import Tokenizer
H=pathlib.Path.home(); OUT=H/'local-inference/diagnostics/context-capacity-20261018';OUT.mkdir(exist_ok=True)
KEY=(H/'.omlx/api-key').read_text().strip();MODEL='gpt-oss-120b-mxfp4-bf16'
tokenizer=Tokenizer.from_file(str(H/'.omlx/models'/MODEL/'tokenizer.json'))
text=os.environ.get('PROBE_PREFIX','')+''.join(f'Record {i:06d}: sample measurement data for local context capacity validation.\n' for i in range(20000))
ids=tokenizer.encode(text,add_special_tokens=False).ids
spec=importlib.util.spec_from_file_location('proc_memory','/Applications/oMLX.app/Contents/Resources/omlx/utils/proc_memory.py')
proc=importlib.util.module_from_spec(spec);spec.loader.exec_module(proc)
pid=int(subprocess.check_output(['pgrep','-x','omlx-server'],text=True).strip())
def call(path,body=None,timeout=15):
 req=urllib.request.Request('http://127.0.0.1:8003'+path,data=json.dumps(body).encode() if body else None,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def sample():
 v=subprocess.check_output(['vm_stat'],text=True);swap=subprocess.check_output(['sysctl','vm.swapusage'],text=True).strip()
 return {'time':time.time(),'vm_stat':v,'swap':swap,'health':call('/health'),'physical_footprint_bytes':proc.get_phys_footprint(pid),'lifetime_peak_bytes':proc.get_lifetime_max_phys_footprint(pid)}
results=[]
for target in json.loads(os.environ.get('PROBE_TARGETS','[32768,65536,130560]')):
 prompt=tokenizer.decode(ids[:target]);actual=len(tokenizer.encode(prompt,add_special_tokens=False).ids)
 row={'target_tokens':target,'tokenizer_count':actual,'samples':[],'started':time.time()};stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:row['samples'].append(sample())
   except Exception as e:row['samples'].append({'error':str(e)})
   stop.wait(3)
 t=threading.Thread(target=monitor,daemon=True);t.start();print('START',target,flush=True)
 try:
  result=call('/v1/completions',{'model':MODEL,'prompt':prompt,'max_tokens':1,'temperature':0,'stream':False},timeout=1800)
  row['usage']=result.get('usage');row['success']=True
 except Exception as e:
  row['success']=False;row['error']=str(e)
  if isinstance(e,urllib.error.HTTPError):row['error_body']=e.read().decode()[:4000]
 finally:stop.set();t.join(timeout=5)
 row['elapsed_seconds']=time.time()-row['started'];results.append(row)
 (OUT/os.environ.get('PROBE_RESULT','results.json')).write_text(json.dumps(results,indent=2)+'\n');print('RESULT',target,row['success'],row.get('usage'),row['elapsed_seconds'],row.get('error'),flush=True)
 if not row['success']:break
