const main=require('./run.js');
const XP={1:0,2:150,3:800,4:2200,5:4500,6:7700,7:13600};
function sv(vm,name){const st=vm.runtime.getTargetForStage(); for(const v of Object.values(st.variables)) if(v.name===name) return v; }
const L=(vm,n)=>sv(vm,n).value;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const lv=+process.argv[3];
 const {vm}=await main(process.argv[2]);
 const mouse=vm.runtime.ioDevices.mouse;
 const post=(x,y,d)=>mouse.postData({x:x+240,y:180-y,isDown:d,canvasWidth:480,canvasHeight:360});
 sv(vm,'xp').value=XP[lv];
 vm.start(); vm.greenFlag(); await sleep(400);
 let problems=[];
 for(let game=0;game<2;game++){
   post(0,-164,false); await sleep(150); post(0,-164,true); await sleep(200); post(0,-164,false); await sleep(300);
   if(+L(vm,'state')!==1){problems.push('no arranca juego '+game); break;}
   const N=+L(vm,'N'); sv(vm,'dbg').value=8;
   const t0=Date.now(); let startFood=0;
   while(+L(vm,'state')===1 && Date.now()-t0<60000){
     await sleep(1000);
     const ex=L(vm,'ex'),ey=L(vm,'ey'),hp=L(vm,'ehp'),dead=L(vm,'edead'),food=L(vm,'efood'),sc=L(vm,'esc');
     let alive=0;
     for(let i=0;i<N;i++){ if(dead[i]==0){alive++; if(!isFinite(+ex[i])||!isFinite(+ey[i])||+ex[i]<0||+ex[i]>+L(vm,'ie')||+ey[i]<0||+ey[i]>+L(vm,'ie')) problems.push(`pos mala e${i} ${ex[i]},${ey[i]}`); if(!isFinite(+hp[i])) problems.push('hp NaN '+i); if(!(+sc[i]>=1&&+sc[i]<=3)) problems.push('esc raro '+i+':'+sc[i]); if(!isFinite(+food[i])) problems.push('food NaN');}}
     if(alive!==+L(vm,'alive')) problems.push(`alive var ${L(vm,'alive')} != real ${alive}`);
   }
   console.log(`lvl ${lv} game ${game}: state ${L(vm,'state')} tick ${L(vm,'tick')} alive ${L(vm,'alive')} rank ${L(vm,'rank')} won ${L(vm,'won')} nCoins ${L(vm,'nCoins')} cfree ${L(vm,'cfree').length} secs ${((Date.now()-t0)/1000)|0}`);
   sv(vm,'dbg').value=0;
   if(+L(vm,'state')!==2){problems.push('no termina la partida (60s)'); break;}
   await sleep(300); post(0,-118,false); await sleep(150); post(0,-118,true); await sleep(200); post(0,-118,false); await sleep(300);
   if(+L(vm,'state')!==0) problems.push('Continue no vuelve al menu');
 }
 console.log(problems.length?('PROBLEMS: '+[...new Set(problems)].slice(0,8).join(' | ')):'OK sin problemas');
 process.exit(0);
})().catch(e=>{console.log('ERR',e);process.exit(1)});
