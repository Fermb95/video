const {chromium}=require('/opt/node-tools/node_modules/playwright');
const {spawn,spawnSync}=require('child_process');
const http=require('http'),fs=require('fs'),path=require('path');
const TM=require('./timemap.json');
const total=TM.K.reduce((a,k,i)=>a+k*(TM.bounds[i+1]-TM.bounds[i]),0);
function sceneT(o){let acc=0;for(let i=0;i<TM.K.length;i++){const d=TM.K[i]*(TM.bounds[i+1]-TM.bounds[i]);if(o<acc+d||i===TM.K.length-1)return TM.bounds[i]+Math.min(o-acc,d)/TM.K[i];acc+=d}}
const FPS=30,NF=Math.round(total*FPS);
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json'};
function serve(){return new Promise(r=>{const sv=http.createServer((q,res)=>{const f=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]).replace(/^\/$/,'/index.html'));
  fs.readFile(f,(e,d)=>{if(e){res.writeHead(404);res.end();return}res.writeHead(200,{'content-type':mime[path.extname(f)]||'application/octet-stream'});res.end(d)})});sv.listen(0,()=>r(sv))})}
async function open(){const sv=await serve();const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1920,height:1080}});await p.goto('http://localhost:'+sv.address().port+'/');await p.waitForFunction('window.ready===true');return {sv,b,p}}
(async()=>{
  const mode=process.argv[2];
  if(mode==='shots'){const {sv,b,p}=await open();for(const t of process.argv[3].split(',').map(Number)){await p.evaluate(t=>seek(t),t);await p.screenshot({path:`${process.env.SHOTS}/g${t}.png`})}await b.close();sv.close();return}
  if(mode==='frames'){const [a,z]=[+process.argv[3],+process.argv[4]];const dir=process.argv[5];const {sv,b,p}=await open();
    for(let i=a;i<z;i++){await p.evaluate(t=>seek(t),Math.min(sceneT(i/FPS),29.999));await p.screenshot({type:'jpeg',quality:95,path:`${dir}/${String(i).padStart(5,'0')}.jpg`})}
    await b.close();sv.close();return}
  if(mode==='all'){const dir=process.argv[3];fs.mkdirSync(dir,{recursive:true});const W=4,per=Math.ceil(NF/W);
    await Promise.all([...Array(W)].map((_,w)=>new Promise(r=>spawn('node',[__filename,'frames',w*per,Math.min(NF,(w+1)*per),dir],{stdio:'inherit'}).on('close',r))));
    console.log('frames',NF)}
})();
