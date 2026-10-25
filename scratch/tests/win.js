const main=require('./run.js');
function sv(vm,name){const st=vm.runtime.getTargetForStage(); for(const v of Object.values(st.variables)) if(v.name===name) return v; }
const L=(vm,n)=>sv(vm,n).value;
main(process.argv[2]).then(async({vm})=>{
  const mouse=vm.runtime.ioDevices.mouse;
  const post=(x,y,down)=>mouse.postData({x:x+240,y:180-y,isDown:down,canvasWidth:480,canvasHeight:360});
  vm.start(); vm.greenFlag();
  await new Promise(r=>setTimeout(r,500));
  post(0,-164,false); await new Promise(r=>setTimeout(r,200)); post(0,-164,true); await new Promise(r=>setTimeout(r,300)); post(0,-164,false);
  await new Promise(r=>setTimeout(r,300));
  const hp=L(vm,'ehp'), mh=L(vm,'emhp');
  hp[0]=1e9; mh[0]=100; for(let i=1;i<50;i++){hp[i]=5;}
  sv(vm,'dbg').value=4;
  for(let k=0;k<30;k++){ await new Promise(r=>setTimeout(r,1000)); const s=+L(vm,'state'); if(+L(vm,'alive')<=3){const h=L(vm,'ehp'); for(let i=1;i<50;i++) if(L(vm,'edead')[i]==0) h[i]=-1;}
 console.log('tick',L(vm,'tick'),'state',s,'alive',L(vm,'alive'),'won',L(vm,'won'),'rank',L(vm,'rank'),'res',L(vm,'resTxt'),'food',(+L(vm,'efood')[0]).toFixed(0),'coins',L(vm,'coins'),'xp',L(vm,'xp')); if(s==2) break; }
  process.exit(0);
});
