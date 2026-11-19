"""Build the three Stardew themes for T3 Code.

    python build.py            # write themes/<id>.json and the background images
    python build.py --install  # also copy them into the T3 Code themes folder

Everything is read from this folder (wiki-assets/, wiki-assets-farm/, art/).
The build stops if a text/background pair falls under WCAG AA contrast.
"""
import json, os, re, shutil, sys
import assets
from assets import build as build_assets, SRC, OUT
AS = build_assets()
THEMES_DIR = os.path.expanduser('~/.t3/userdata/themes')
CSS_LIMIT = 50000

def roles(p):
    g = p.get
    return {
     "canvas":p['canvas'],"chrome":p['toolbar'],"toolbar":p['toolbar'],"toolbarForeground":p['text'],"toolbarBorder":p['line'],
     "toolbarControl":g('tctrl',p['surface']),"toolbarControlForeground":p['text'],"toolbarControlHover":g('tctrlh',p['raised']),
     "surface":p['surface'],"surfaceRaised":p['raised'],"surfaceOverlay":p['raised'],"text":p['text'],"textMuted":p['muted'],
     "border":p['line'],"input":p['raised'],"focus":p['accent'],"accent":p['accent'],"accentForeground":g('accentFg','#ffffff'),
     "secondary":p['chip'],"secondaryForeground":p['text'],"muted":p['chip'],"mutedForeground":p['muted'],"placeholder":g('placeholder',p['muted']),
     "secondaryLabel":p['muted'],"iconMuted":p['muted'],
     "error":g('error','#cf3d28'),"errorForeground":g('errorFg','#ffffff'),"errorSurface":g('errorS','#fbe0da'),
     "warning":g('warning','#e58a2a'),"warningForeground":g('warningFg','#2b1a05'),"warningSurface":g('warningS','#fdebd2'),
     "update":p['update'],"updateForeground":g('updateFg','#ffffff'),"updateSurface":g('updateS',p['chip']),
     "accentSurface":g('accentS',p['chip']),"accentSurfaceForeground":p['head'],
     "messageSurface":p['msg'],"messageForeground":p['text'],"messageAction":p['chip'],"messageActionForeground":p['text'],"messageActionHover":p['line'],
     "codeBackground":p['code'],"codeForeground":p['text'],
     "searchMatchBackground":"#ffe08a","searchMatchForeground":"#2b2b2b","searchMatchActiveBackground":"#f7a072","searchMatchActiveForeground":"#1f1f1f",
     "sidebar":p['side'],"sidebarForeground":g('sfg',p['text']),"sidebarMutedForeground":g('smuted',p['muted']),
     "sidebarControlSurface":g('sctrl',p['raised']),"sidebarRowHover":p['shover'],"sidebarRowActive":p['sactive'],"sidebarRowSelected":p['sactive'],"sidebarBorder":g('sline',p['line']),
     "terminalBackground":p['term'],"terminalForeground":g('termfg','#e8f0f2'),"terminalCursor":p['update'],"terminalSelection":p['accent']+"55",
     "terminalScrollbar":"#3a4a5a","terminalScrollbarHover":"#56697c"}

def kvars(p):
    g=p.get
    v={'k-accent':p['btn'],'k-accent2':p['btn2'],'k-accent3':p['btn3'],'k-btn':g('btnfg','#fff'),'k-line':p['line'],'k-frame':g('frame',p['line']),
       'k-card':p['raised'],'k-ink':p['text'],'k-mu':p['muted'],'k-head':p['head'],'k-link':g('link',p['head']),'k-chip':p['chip'],
       'k-shadow':g('shadow','rgba(20,60,80,.12)'),'k-off':g('off',p['chip']),'k-offi':p['muted'],'k-side':p['side'],
       'k-scard':g('scard',p['raised']),'k-sline':g('sline2',p['line']),'k-sfg':g('sfg',p['text']),'k-smu':g('smuted',p['muted'])}
    v.update(g('extra',{}))
    return ';'.join('--%s:%s'%kv for kv in v.items())

# Selectors: only data-* / aria / href attributes and the class names the theme guide lists as
# stable (.chat-markdown, .chat-markdown-codeblock, .composer-tiptap). No Tailwind utility classes.
# $ROW$ is the sidebar row that holds the search box and the icon buttons; "New thread" is its last button.
ROW='[data-workspace-area=sidebar] [data-slot=sidebar-group]>div:has(>div>[data-slot=input-control])'
SEND='[data-chat-composer-form] :is(button[type=submit],[data-chat-composer-actions]>button:last-child,[data-chat-composer-actions]>span:last-child>button)'

BASE = r'''
:root{--k-art:0px;%(L)s}.dark{%(D)s}
body{font-family:ui-rounded,"SF Pro Rounded",-apple-system,BlinkMacSystemFont,"PingFang SC",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
svg.lucide{stroke-width:1.9}
[data-slot=sidebar-inner] a[href="/"]{width:auto!important;&>*{display:none!important}&::before{content:"";display:block;width:$logo_w$px;height:30px;background:url($logo$) left center/contain no-repeat}}
$ROW${flex-wrap:wrap!important;row-gap:8px!important;
&>div:has(>[data-slot=input-control]){height:34px!important;border-radius:10px!important;background:var(--k-scard)!important;border:1.5px solid var(--k-sline)!important;font-weight:500!important;&:focus-within{border-color:var(--k-accent)!important;box-shadow:0 0 0 3px color-mix(in srgb,var(--k-accent) 22%%,transparent)!important}}
&>div:not(:has(>[data-slot=input-control])){display:contents!important}
&>div>button[data-sidebar=menu-button]:last-of-type{order:9;flex:1 1 100%%!important;width:100%%!important;height:38px!important;justify-content:center!important;gap:8px!important;padding:0 12px!important;border-radius:10px!important;background:var(--k-accent)!important;color:var(--k-btn)!important;font-size:14px!important;font-weight:700!important;letter-spacing:.01em;box-shadow:0 3px 0 var(--k-accent3)!important;transition:transform .06s,background-color .12s;&:hover{background:var(--k-accent2)!important}&:active{transform:translateY(2px);box-shadow:0 1px 0 var(--k-accent3)!important}&>*{display:none!important}&::before{content:"";flex:none;width:22px;height:22px;background:url($newicon$) center/contain no-repeat;image-rendering:pixelated}&::after{content:attr(aria-label)}}}
[data-slot=sidebar]{font-size:14px}
[data-thread-item]{padding-top:2px!important;padding-bottom:2px!important}
[data-testid=sidebar-row-card]{border-radius:10px!important;& span[dir]{font-weight:500!important}&[aria-current]{background:var(--k-scard)!important;box-shadow:inset 3px 0 0 var(--k-accent),inset 0 0 0 1.5px var(--k-sline)!important;--tw-ring-color:transparent!important}}
[data-slot=project-monogram]{border-radius:5px;overflow:hidden}
[data-sidebar-row^="shelf:"]{border-radius:9px!important;font-weight:600!important}
[data-slot=sidebar-inner]{padding-bottom:var(--k-art)!important;position:relative}
[data-chat-header]{border-bottom:1.5px solid var(--k-line)!important;box-shadow:none!important}
[data-workspace-area=conversation]>[data-timeline-loading]{background:transparent!important}
[data-chat-composer-stack] h1{position:relative;&::before{content:"";position:absolute;left:50%%;bottom:calc(100%% + 22px);margin-left:-27px;width:54px;height:54px;background:url($hero$) center/contain no-repeat;image-rendering:pixelated;animation:kbob 2.4s ease-in-out infinite}}
@keyframes kbob{50%%{transform:translateY(-5px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
h1 [data-draft-project-trigger]{color:var(--k-link)!important}
.chat-markdown{font-size:15px!important;line-height:1.65!important;
& :is(h1,h2,h3,h4){color:var(--k-head)!important;font-weight:700!important}
& h1{font-size:21px!important}& h2{font-size:18px!important;padding-bottom:.3em;border-bottom:2px dotted var(--k-line)}& :is(h3,h4){font-size:16px!important}
& strong{font-weight:700}& li::marker{color:var(--k-head)}
& a[href^=http]:not([data-markdown-image-link],[data-footnote-ref],[data-footnote-backref],:has([data-slot=context-chip-label])){color:var(--k-link)!important;background:none!important;text-decoration:underline;text-decoration-color:color-mix(in srgb,currentColor 40%%,transparent);text-underline-offset:2px}
& code:not(pre code){border-radius:5px;padding:.12em .4em;font-size:.86em;background:var(--k-chip)!important;border:1px solid var(--k-line)!important;color:var(--k-head)}
& blockquote{border-left:3px solid var(--k-accent)!important;background:var(--k-chip);border-radius:0 8px 8px 0;padding:6px 12px!important;color:var(--k-mu)}
& table{font-size:14px}& th{color:var(--k-head)!important;font-weight:700!important;border-bottom:2px solid var(--k-line)!important}& td{border-color:var(--k-line)!important}
& tbody tr:hover td{background:color-mix(in srgb,var(--k-chip) 60%%,transparent)}
& hr{border:none!important;height:2px;background:repeating-linear-gradient(90deg,var(--k-line) 0 6px,transparent 6px 10px)}}
.chat-markdown-codeblock{border-radius:10px!important;border:1.5px solid var(--k-line)!important;font-size:13px}
[data-user-message-bubble]{border-radius:14px 14px 4px 14px!important;padding:10px 15px!important;font-size:15px!important;line-height:1.55!important;border:1.5px solid var(--k-line)!important;box-shadow:0 2px 0 var(--k-line)!important}
[data-timeline-row-kind=work]{font-size:14px;color:var(--k-mu)}
[data-slot=composer-host]{border-radius:16px!important;border:1.5px solid var(--k-frame)!important;box-shadow:0 3px 0 var(--k-line),0 10px 28px var(--k-shadow)!important;background:var(--k-card)!important;&:focus-within{box-shadow:0 3px 0 var(--k-line),0 0 0 3px color-mix(in srgb,var(--k-frame) 35%%,transparent),0 10px 28px var(--k-shadow)!important}}
:is([data-slot=composer-host],[data-chat-composer-main-surface])::after{display:none!important}
.composer-tiptap{font-size:15px!important;line-height:1.5!important}
$SEND${background:var(--k-accent)!important;color:var(--k-btn)!important;border:none!important;box-shadow:0 2px 0 var(--k-accent3)!important;&>span:empty{display:none!important}& svg{color:var(--k-btn)!important;stroke:var(--k-btn)!important}&:hover:not(:disabled){background:var(--k-accent2)!important}&:active:not(:disabled){transform:translateY(1px);box-shadow:0 1px 0 var(--k-accent3)!important}&:disabled{background:var(--k-off)!important;box-shadow:none!important;opacity:1!important;& svg{color:var(--k-offi)!important;stroke:var(--k-offi)!important}}}
:is([data-slot=dialog-popup],[data-slot=command-dialog-popup]){border-radius:16px!important;border:1.5px solid var(--k-frame)!important}
:is([data-slot=popover-popup],[data-slot=menu-popup]){border-radius:12px!important;border:1.5px solid var(--k-frame)!important;box-shadow:0 3px 0 var(--k-line),0 12px 30px var(--k-shadow)!important}
[data-slot=tooltip-popup]{border-radius:7px!important;font-size:12px}
[data-thread-details-card]{border-radius:14px!important;border:1.5px solid var(--k-frame)!important;box-shadow:0 3px 0 var(--k-line),0 10px 26px var(--k-shadow)!important}
[data-slot=button]{border-radius:8px}:is([data-slot=input],[data-slot=select-trigger]){border-radius:8px}
[data-slot=switch]{background:color-mix(in srgb,var(--k-mu) 42%%,transparent)!important;&[data-checked]{background:var(--k-head)!important}&>[data-slot=switch-thumb]{background:#fff!important;box-shadow:0 1px 2px rgba(0,0,0,.35)!important}}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:color-mix(in srgb,var(--k-mu) 38%%,transparent);border-radius:10px;border:3px solid transparent;background-clip:content-box}
[data-slot=scroll-area-thumb]{background:color-mix(in srgb,var(--k-mu) 40%%,transparent)!important}
'''
# Sidebar artwork: scales with the sidebar, never taller than 19% of the window, gone on short windows
# so it cannot push the thread list and the Working / Settled shelves out of reach.
ART=r'''@media (min-height:640px){[data-slot=sidebar-inner]{--k-art:min(calc(%s),19vh)}}'''

ISLAND_L=dict(canvas='#f6fcfc',toolbar='#d5f0f3',surface='#fbfefe',raised='#ffffff',text='#17384a',muted='#4f7280',line='#b7dde3',accent='#0a7c87',
 chip='#e2f4f6',update='#c9452a',updateS='#fde5dd',msg='#d9f1f3',code='#ecf7f8',side='#dff4f5',smuted='#4a6d7b',shover='#eaf8f9',sactive='#ffffff',term='#0f2433',
 head='#0b6f7a',btn='#c9452a',btn2='#b83b21',btn3='#8f2c17',frame='#7cc7d0',shadow='rgba(20,90,110,.14)')
ISLAND_D=dict(canvas='#0c1a2a',toolbar='#0f2437',surface='#12283b',raised='#173349',text='#e2f1f4',muted='#8fb0bc',line='#24465c',accent='#2cc4cf',accentFg='#04262a',
 chip='#16334a',update='#f7937a',updateFg='#3a1208',updateS='#4a2218',errorS='#4a1f18',warningS='#4a3518',msg='#16405a',code='#0a1520',side='#0f2437',shover='#16334a',sactive='#1b3f59',term='#0a1520',
 head='#7fe3ea',btn='#c9452a',btn2='#dc5637',btn3='#7a2614',frame='#2f6f85',shadow='rgba(0,0,0,.45)')
ISLAND_CSS=ART%'var(--sidebar-width,300px)*.6133'+r'''
[data-slot=sidebar-inner]{border-right:1.5px solid var(--k-line)!important;&::after{content:"";position:absolute;left:0;right:0;bottom:0;height:var(--k-art);pointer-events:none;background:linear-gradient(to bottom,var(--k-side) 0,transparent 44px),var(--theme-background-image) center bottom/cover no-repeat}}
.dark [data-slot=sidebar-inner]::after{background:linear-gradient(to bottom,var(--k-side) 0,rgba(15,36,55,.35) 44px,rgba(8,20,40,.45)),var(--theme-background-image) center bottom/cover no-repeat}
[data-workspace-area=conversation]{background-image:radial-gradient(120%% 70px at 30%% 100%%,#bfe9ee 0,transparent 70%%),radial-gradient(90%% 46px at 78%% 100%%,#d3f1f3 0,transparent 72%%),linear-gradient(to top,#cfeef2 0,transparent 300px)!important}
.dark [data-workspace-area=conversation]{background-image:radial-gradient(2px 2px at 9%% 12%%,#f7e7a8 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 21%% 31%%,#fffc 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 33%% 7%%,#fff 50%%,transparent 51%%),radial-gradient(2px 2px at 47%% 19%%,#bfe9ffcc 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 58%% 5%%,#fffb 50%%,transparent 51%%),radial-gradient(2px 2px at 69%% 24%%,#f7e7a8cc 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 81%% 9%%,#fff 50%%,transparent 51%%),radial-gradient(2px 2px at 93%% 28%%,#bfe9ffcc 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 4%% 41%%,#fff9 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 96%% 47%%,#fff9 50%%,transparent 51%%),linear-gradient(to top,#123a52 0,transparent 260px)!important}
:is([data-slot=composer-host],[data-thread-details-card]){background:color-mix(in srgb,var(--k-card) 68%%,transparent)!important;backdrop-filter:blur(14px) saturate(1.25);-webkit-backdrop-filter:blur(14px) saturate(1.25)}
[data-chat-composer-main-surface]{background:transparent!important;box-shadow:none!important}
[data-sidebar-row="shelf:working"]::before{content:"";flex:none;width:14px;height:14px;background:url($bobber$) center/contain no-repeat;image-rendering:pixelated;animation:kbob 1.2s ease-in-out infinite}
'''

MENU_L=dict(canvas='#ffeccb',toolbar='#ffc677',surface='#fff3d9',raised='#fff8e6',text='#5b2b2a',muted='#84482b',line='#dba05c',accent='#2f7a22',
 chip='#ffdfa8',update='#d6362b',updateS='#fbd9c8',msg='#ffd596',code='#fff3d9',side='#ffd596',shover='#ffe2b4',sactive='#fff3d9',term='#2b1b14',termfg='#ffe2b0',
 head='#8a3a05',link='#a84a05',btn='#2f7a22',btn2='#38902a',btn3='#1c4f13',frame='#b14e05',shadow='rgba(91,43,42,.22)',sline2='#c98a45',
 extra={'k-parch':'#ffeccb','k-panel':'#ffdca8','k-f1':'#5b2b2a','k-f2':'#b14e05','k-f3':'#dc7b05','k-sky':'linear-gradient(#2f93ee,#62e4e3)'})
MENU_D=dict(canvas='#33241d',toolbar='#2a1c16',surface='#3c2b22',raised='#463228',text='#ffe2b0',muted='#c9a57c',line='#6b4a2c',accent='#6cc24a',accentFg='#12240a',
 chip='#4a352a',update='#ff7a5c',updateFg='#3a1208',updateS='#4a2218',errorS='#4a1f18',warningS='#4a3518',msg='#553c2c',code='#241812',side='#2a1c16',shover='#3a2920',sactive='#4a352a',term='#1c120d',termfg='#ffe2b0',
 head='#ffc677',link='#ffb35a',btn='#2f7a22',btn2='#38902a',btn3='#163f0f',frame='#b14e05',shadow='rgba(0,0,0,.5)',sline2='#7a5230',
 extra={'k-parch':'#33241d','k-panel':'#463228','k-f1':'#1d0f0c','k-f2':'#8a3d06','k-f3':'#b86505',
  'k-sky':'radial-gradient(1.5px 1.5px at 6% 12%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 14% 34%,#fffc 50%,transparent 51%),radial-gradient(1.5px 1.5px at 91% 18%,#ffe9a0 50%,transparent 51%),radial-gradient(1px 1px at 96% 44%,#fffa 50%,transparent 51%),radial-gradient(1px 1px at 4% 62%,#fff9 50%,transparent 51%),linear-gradient(#0b1030,#14224f 60%,#23457c)'})
# --kl is half the width of the parchment page and --kc its centre. Both follow the app's own
# --chat-lane-inset-* variables, so the page stays under the chat column when side panels open.
MENU_CSS=ART%'(var(--sidebar-width,300px) - 6px)*.6563'+r'''
[data-workspace-area=conversation]{--kl:min(calc(var(--chat-content-max-width,46rem)/2 + 20px),calc((100% - var(--chat-lane-inset-start,0px) - var(--chat-lane-inset-end,0px))/2 - 15px));--kc:calc(50%% + (var(--chat-lane-inset-start,0px) - var(--chat-lane-inset-end,0px))/2);background:linear-gradient(90deg,transparent calc(var(--kc) - var(--kl) - 9px),var(--k-f1) 0 calc(var(--kc) - var(--kl) - 6px),var(--k-f2) 0 calc(var(--kc) - var(--kl) - 3px),var(--k-f3) 0 calc(var(--kc) - var(--kl)),var(--k-parch) 0 calc(var(--kc) + var(--kl)),var(--k-f3) 0 calc(var(--kc) + var(--kl) + 3px),var(--k-f2) 0 calc(var(--kc) + var(--kl) + 6px),var(--k-f1) 0 calc(var(--kc) + var(--kl) + 9px),transparent 0),var(--k-sky)!important}
[data-slot=sidebar-inner]{border-right:3px solid var(--k-f1)!important;box-shadow:inset -3px 0 0 var(--k-f3),inset -6px 0 0 var(--k-f2)!important;&::after{content:"";position:absolute;left:0;right:6px;bottom:0;height:var(--k-art);box-sizing:border-box;pointer-events:none;border-top:3px solid var(--k-f1);box-shadow:inset 0 3px 0 var(--k-f3);background:var(--theme-background-image) center bottom/cover no-repeat;image-rendering:pixelated}}
@media (max-height:639px){[data-slot=sidebar-inner]::after{display:none}}
.dark [data-slot=sidebar-inner]::after{background:linear-gradient(rgba(10,16,50,.42),rgba(10,16,50,.42)),var(--theme-background-image) center bottom/cover no-repeat}
[data-chat-header]{border-bottom:3px solid var(--k-f1)!important;box-shadow:inset 0 -3px 0 var(--k-f3)!important}
:is([data-slot=composer-host],[data-thread-details-card],[data-slot=dialog-popup],[data-slot=command-dialog-popup]){border:13px solid transparent!important;border-image:url($menu$) 15/13px stretch!important;border-radius:0!important;background-color:var(--k-panel)!important;background-clip:padding-box!important;box-shadow:0 8px 24px var(--k-shadow)!important}
:is([data-slot=popover-popup],[data-slot=menu-popup],[data-slot=toast-viewport]>*,[data-slot=toast-viewport-anchored]>*){border:3px solid var(--k-f2)!important;border-radius:5px!important;background-color:var(--k-panel)!important;box-shadow:0 0 0 2px var(--k-f1),inset 0 0 0 2px var(--k-f3),0 8px 24px var(--k-shadow)!important;backdrop-filter:none!important}
[data-slot=tooltip-popup]{border-radius:4px!important;border:2px solid var(--k-f1)!important}
[data-chat-composer-main-surface]{background:transparent!important;box-shadow:none!important}
[data-user-message-bubble]{border-radius:6px!important;border:3px solid var(--k-f2)!important;box-shadow:0 0 0 2px var(--k-f1),inset 0 0 0 2px var(--k-f3)!important}
[data-testid=sidebar-row-card]{border-radius:6px!important;&[aria-current]{box-shadow:inset 0 0 0 2px var(--k-f2),inset 0 0 0 4px var(--k-f3)!important}}
$ROW$>div>button[data-sidebar=menu-button]:last-of-type{border-radius:6px!important;border:2px solid var(--k-accent3)!important}
[data-sidebar-row="shelf:working"]::before{content:"";flex:none;width:18px;height:18px;background:url($junimo$) center/contain no-repeat;image-rendering:pixelated}
.chat-markdown-codeblock{border-radius:6px!important;border:2px solid var(--k-f2)!important}
'''

COVER_L=dict(canvas='#f7fbff',toolbar='#eaf4ff',surface='#fbfdff',raised='#ffffff',text='#1c2b4a',muted='#5a6b88',line='#cfdff2',accent='#2a70c2',
 chip='#e6f1fd',update='#e58a12',updateFg='#3a2100',updateS='#fdebd2',msg='#dcecff',code='#eef5fc',side='#1b2a8a',sfg='#ffffff',smuted='#e3ebff',sctrl='#ffffff24',shover='#ffffff1f',sactive='#ffffff33',sline='#0f1a4a',term='#0f1430',
 head='#1f5fc4',btn='#f6c02e',btn2='#ffd04a',btn3='#b9840c',btnfg='#4a2a00',frame='#9cc4ee',shadow='rgba(20,50,110,.18)',scard='rgba(255,255,255,.16)',sline2='rgba(255,255,255,.3)',
 extra={'k-veil':'rgba(247,251,255,.3)','k-lane':'rgba(250,253,255,.95)','k-glass':'rgba(255,255,255,.86)'})
COVER_D=dict(canvas='#0f1430',toolbar='#121a3d',surface='#151c42',raised='#1a2350',text='#eef3ff',muted='#9fb0d6',line='#2a3566',accent='#6db3ff',accentFg='#06183a',
 chip='#1d2858',update='#f6c02e',updateFg='#3a2100',updateS='#4a3a12',errorS='#4a1f18',warningS='#4a3518',msg='#22306e',code='#0b1026',side='#130d4b',sfg='#ffffff',smuted='#c5d4f5',sctrl='#ffffff1f',shover='#ffffff1a',sactive='#ffffff2e',sline='#080a2a',term='#0b1026',
 head='#8cc4ff',btn='#f6c02e',btn2='#ffd04a',btn3='#8a6208',btnfg='#3a2100',frame='#3a4a8f',shadow='rgba(0,0,0,.5)',scard='rgba(255,255,255,.12)',sline2='rgba(255,255,255,.22)',
 extra={'k-veil':'rgba(8,12,36,.5)','k-lane':'rgba(13,18,46,.93)','k-glass':'rgba(22,30,72,.88)'})
COVER_CSS=r'''
@media (min-height:640px){[data-slot=sidebar-inner]{--k-art:min(128px,17vh)}}
[data-workspace-area=conversation]{--kl:min(calc(var(--chat-content-max-width,46rem)/2 + 26px),calc((100% - var(--chat-lane-inset-start,0px) - var(--chat-lane-inset-end,0px))/2 - 8px));--kc:calc(50%% + (var(--chat-lane-inset-start,0px) - var(--chat-lane-inset-end,0px))/2);background:linear-gradient(90deg,transparent calc(var(--kc) - var(--kl)),var(--k-lane) 0 calc(var(--kc) + var(--kl)),transparent 0),linear-gradient(var(--k-veil),var(--k-veil)),var(--theme-background-image) center bottom/cover no-repeat!important}
[data-workspace-area=conversation]:has(>[data-timeline-loading]){background:linear-gradient(var(--k-veil),var(--k-veil)),var(--theme-background-image) center bottom/cover no-repeat!important}
[data-slot=sidebar-inner]{background:linear-gradient(180deg,#130d4b 0,#1a2a8c 34%%,#1c4fb0 70%%,#1f6cc0 100%%)!important;border-right:none!important;&::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(1.5px 1.5px at 18%% 3%%,#fff 50%%,transparent 51%%),radial-gradient(1px 1px at 62%% 6%%,#fffc 50%%,transparent 51%%),radial-gradient(1.5px 1.5px at 84%% 2.5%%,#ffe9a0 50%%,transparent 51%%),radial-gradient(1px 1px at 40%% 9%%,#fffa 50%%,transparent 51%%),radial-gradient(1px 1px at 92%% 12%%,#fff9 50%%,transparent 51%%)}&::after{content:"";position:absolute;left:0;right:0;bottom:0;height:var(--k-art);pointer-events:none;background:url($coop$) center bottom 6px/auto calc(100%% - 12px) no-repeat,linear-gradient(to top,#3f7f1e 0 6px,#5aa02c 6px 22px,transparent 22px)}}
@media (max-height:639px){[data-slot=sidebar-inner]::after{display:none}}
[data-slot=sidebar]{& svg.lucide{color:var(--k-sfg)}& [data-testid=sidebar-row-card]{color:#fff!important;& span[dir]{color:#fff!important}& span:not([dir],[data-slot=project-monogram],[data-slot=project-monogram] *){color:var(--k-smu)!important}}& [data-sidebar-row^="shelf:"]{color:#fff!important;& span{color:#fff!important}}& [data-slot=project-monogram]{box-shadow:0 0 0 1px #fff8}}
[data-slot=sidebar] input::placeholder{color:var(--k-smu)!important}
[data-chat-header]{background:var(--k-glass)!important;backdrop-filter:blur(14px)}
[data-slot=composer-host]{background:var(--k-glass)!important;backdrop-filter:blur(16px) saturate(1.3)}
[data-chat-composer-stack]:has(h1) h1{text-shadow:0 1px 0 var(--k-glass),0 0 18px var(--k-glass),0 0 6px var(--k-glass)}
[data-chat-composer-stack] h1~button{background:var(--k-glass)!important;color:var(--k-ink)!important;padding:3px 12px!important;border-radius:999px!important}
[data-sidebar-row="shelf:working"]::before{content:"";flex:none;width:18px;height:18px;background:url($junimo$) center/contain no-repeat;image-rendering:pixelated}
'''

THEMES={
 'stardew-island':dict(name='星露谷 · 海岛码头',L=ISLAND_L,D=ISLAND_D,css=ISLAND_CSS,newicon='pole',hero='fish',bg='stardew-island.jpg'),
 'stardew-menu':dict(name='星露谷 · 游戏菜单',L=MENU_L,D=MENU_D,css=MENU_CSS,newicon='stardrop',hero='stardrop',bg='stardew-menu.png'),
 'stardew-cover':dict(name='星露谷 · 封面',L=COVER_L,D=COVER_D,css=COVER_CSS,newicon='stardrop',hero='junimo',bg='stardew-cover.png'),
}

def _lum(h):
    h=h.lstrip('#')[:6]; r=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    r=[c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4 for c in r]; return .2126*r[0]+.7152*r[1]+.0722*r[2]
def contrast(a,b):
    a,b=_lum(a),_lum(b); a,b=max(a,b),min(a,b); return (a+.05)/(b+.05)
PAIRS=[('text','canvas'),('textMuted','canvas'),('textMuted','surface'),('accentForeground','accent'),('accent','canvas'),
 ('sidebarForeground','sidebar'),('sidebarMutedForeground','sidebar'),('messageForeground','messageSurface'),('placeholder','input'),
 ('updateForeground','update'),('warningForeground','warning'),('errorForeground','error'),('toolbarForeground','toolbar'),
 ('terminalForeground','terminalBackground'),('codeForeground','codeBackground')]
def audit(tid,t):
    bad=[]
    for mode,p in (('light',t['L']),('dark',t['D'])):
        c=roles(p)
        pairs=[(a,b,c[a],c[b]) for a,b in PAIRS]+[('button label','button',p.get('btnfg','#ffffff'),p['btn']),('heading','canvas',p['head'],p['canvas']),('link','canvas',p.get('link',p['head']),p['canvas'])]
        for a,b,x,y in pairs:
            if x.startswith('#') and y.startswith('#') and contrast(x,y)<4.5: bad.append('%s %s: %s on %s = %.2f'%(tid,mode,a,b,contrast(x,y)))
    return bad

def make(tid):
    t=THEMES[tid]
    css=(BASE+t['css']).replace('%(L)s',kvars(t['L'])).replace('%(D)s',kvars(t['D'])).replace('%%','%')
    sub=dict(AS); sub['newicon']='$%s$'%t['newicon']; sub['hero']='$%s$'%t['hero']; sub['logo_w']='%g'%sub['logo_w']; sub['ROW']=ROW; sub['SEND']=SEND
    css=css.replace('$newicon$',sub['newicon']).replace('$hero$',sub['hero'])
    used={}
    def put(m):
        v=str(sub[m.group(1)])
        if not v.startswith('data:'): return v
        used[m.group(1)]=v; return 'var(--s-%s)'%m.group(1)
    css=re.sub(r'url\(\$(\w+)\$\)',put,css)          # each sprite is stored once, as a custom property
    css=re.sub(r'\$(\w+)\$',lambda m:str(sub[m.group(1)]),css)
    css=':root{'+';'.join('--s-%s:url(%s)'%kv for kv in used.items())+'}'+css
    css=re.sub(r'\n+','',css)
    L=roles(t['L']); D=roles(t['D'])
    return dict(version=1,name=t['name'],appearance='light',canvas=L['canvas'],accent=L['accent'],colors=L,variants={'dark':D},css=css)

if __name__=='__main__':
    bad=[b for tid,t in THEMES.items() for b in audit(tid,t)]
    if bad: sys.exit('Contrast under 4.5:\n  '+'\n  '.join(bad))
    assets.backgrounds()
    for tid,t in THEMES.items():
        th=make(tid); n=len(th['css'])
        if n>CSS_LIMIT: sys.exit('%s: css is %d characters, limit %d'%(tid,n,CSS_LIMIT))
        json.dump(th,open(OUT+tid+'.json','w'),ensure_ascii=False)
        print('%s  css %d chars (%d%% of limit), embedded sprites %d'%(tid,n,100*n//CSS_LIMIT,sum(len(m) for m in re.findall(r'url\(data:[^)]*\)',th['css']))))
    if '--install' in sys.argv:
        for tid,t in THEMES.items():
            for f in (tid+'.json',t['bg']): shutil.copyfile(OUT+f,os.path.join(THEMES_DIR,f))
        print('installed to',THEMES_DIR)
