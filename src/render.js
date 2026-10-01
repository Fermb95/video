const {chromium}=require('/opt/node-tools/node_modules/playwright');
const {spawn}=require('child_process');
const path=require('path');
(async()=>{
  const FPS=30,DUR=30,out=process.argv[2]||'hefame-joule.mp4';
  const only=process.argv[3]?process.argv[3].split(',').map(Number):null;
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p=await b.newPage({viewport:{width:1920,height:1080}});
  await p.goto('file://'+path.resolve(__dirname,'index.html'));
  if(only){for(const t of only){await p.evaluate(t=>seek(t),t);await p.screenshot({path:`${process.env.SHOTS}/f${t}.png`});}await b.close();return;}
  const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','medium','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<FPS*DUR;i++){
    await p.evaluate(t=>seek(t),i/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
})();
