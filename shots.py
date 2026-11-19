"""Screenshot a built theme in a headless Chrome that is paired with the local T3 Code server.

    python shots.py <themeId> <light|dark> <tag> [extra-steps.json]

Env: THREAD_URL (required), SIZE=WxH, PAGE_JS=<file>.

Needs Chrome started with --remote-debugging-port=9333 (see README). Writes shots/<tag>-*.png.
The theme is injected into the page, so it does not have to be installed first.
"""
import json,sys,base64,subprocess,os
SRC=os.path.dirname(os.path.abspath(__file__)); os.chdir(SRC); os.makedirs('shots',exist_ok=True)
tid,mode,tag=sys.argv[1:4]
th=json.load(open('themes/%s.json'%tid))
bg=''
for ext,mime in (('jpg','image/jpeg'),('png','image/png')):
    p='themes/%s.%s'%(tid,ext)
    if os.path.exists(p): bg='data:%s;base64,%s'%(mime,base64.b64encode(open(p,'rb').read()).decode())
apply='''(()=>{const th=%s,dark=%s,bg=%s;const r=document.documentElement;r.classList.toggle('dark',dark);
const c=dark?{...th.colors,...th.variants.dark}:th.colors;
for(const [k,v] of Object.entries(c)){let n=k.replace(/[A-Z]/g,m=>'-'+m.toLowerCase());if(n==='terminal-selection')n='terminal-selection-background';r.style.setProperty('--app-theme-'+n,v)}
r.style.backgroundColor=c.chrome;r.style.setProperty('--theme-background-image',bg?'url('+bg+')':'none');
let s=window.__ks; if(!s){s=new CSSStyleSheet();window.__ks=s;document.adoptedStyleSheets=[s]} s.replaceSync(th.css);return s.cssRules.length})()'''%(json.dumps(th),'true' if mode=='dark' else 'false',json.dumps(bg))
W,H=[int(x) for x in os.environ.get('SIZE','1440x900').split('x')]
dismiss="[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Dismiss')?.click()"
T=os.environ.get('THREAD_URL') or sys.exit('set THREAD_URL to the address of a thread to screenshot')
# PAGE_JS: optional script run in the page after the theme is applied (e.g. to replace private text before a public screenshot)
if os.environ.get('PAGE_JS'): apply='(()=>{const r=%s;%s;return r})()'%(apply,open(os.environ['PAGE_JS']).read())
steps=[{"size":[W,H]},{"eval":"location.href===%s||(location.href=%s)"%(json.dumps(T),json.dumps(T)),"sleep":4000},{"eval":dismiss},{"eval":apply,"print":True},{"sleep":900},{"shot":"shots/%s-chat.png"%tag},
 {"eval":"document.querySelector('.messages-timeline-scroll').scrollTop=0","sleep":900},{"shot":"shots/%s-top.png"%tag},
 {"eval":"document.querySelector('[data-slot=sidebar-inner] a[href]').click()","sleep":1800},{"shot":"shots/%s-draft.png"%tag}]
if len(sys.argv)>4: steps+=json.load(open(sys.argv[4]))
json.dump(steps,open('shots/_steps.json','w'))
print(subprocess.run(['node','cdp.mjs','shots/_steps.json'],capture_output=True,text=True).stdout[-300:])
