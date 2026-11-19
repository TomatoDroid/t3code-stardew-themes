// usage: node cdp.mjs <json-steps-file>
import fs from 'node:fs';
const steps = JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const port = 9333;
const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
let t = targets.find(x=>x.type==='page');
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let id=0; const pend=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id)}};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend.set(i,r);ws.send(JSON.stringify({id:i,method,params}))});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await send('Page.enable'); await send('Runtime.enable');
for(const s of steps){
  if(s.size) await send('Emulation.setDeviceMetricsOverride',{width:s.size[0],height:s.size[1],deviceScaleFactor:s.scale||1,mobile:false});
  if(s.scheme) await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:s.scheme}]});
  if(s.goto){await send('Page.navigate',{url:s.goto});await sleep(s.wait||2500)}
  if(s.eval){const r=await send('Runtime.evaluate',{expression:s.eval,awaitPromise:true,returnByValue:true}); if(s.print) console.log(JSON.stringify(r.result?.result?.value ?? r.result?.exceptionDetails?.exception?.description ?? r, null, 1))}
  if(s.type){await send('Input.insertText',{text:s.type})}
  if(s.key){for(const type of ['keyDown','keyUp']) await send('Input.dispatchKeyEvent',{type,key:s.key,code:s.key,windowsVirtualKeyCode:s.vk||13})}
  if(s.click){for(const type of ['mousePressed','mouseReleased']) await send('Input.dispatchMouseEvent',{type,x:s.click[0],y:s.click[1],button:'left',clickCount:1})}
  if(s.move){await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:s.move[0],y:s.move[1]})}
  if(s.sleep) await sleep(s.sleep);
  if(s.shot){const o=s.clip?{clip:{x:s.clip[0],y:s.clip[1],width:s.clip[2],height:s.clip[3],scale:1}}:{};const r=await send('Page.captureScreenshot',{format:'png',...o});fs.writeFileSync(s.shot,Buffer.from(r.result.data,'base64'));console.log('shot',s.shot)}
}
ws.close();
