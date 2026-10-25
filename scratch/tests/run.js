const fs=require('fs');
const VirtualMachine=require('scratch-vm');
let Storage=require('scratch-storage'); Storage=Storage.ScratchStorage;
global.window = global; 
async function main(file, frames){
  const vm=new VirtualMachine();
  const storage=new Storage();
  vm.attachStorage(storage);
  // fake renderer
  const calls={stamp:0,line:0,point:0,clear:0};
  let nextId=1;
  const fake={
    _nextDrawableId:1,
    createDrawable(){return nextId++;}, destroyDrawable(){}, createPenSkin(){return 99;}, createBitmapSkin(){return nextId++;},
    createSVGSkin(){return nextId++;}, updateDrawableSkinId(){}, updateDrawablePosition(){}, updateDrawableDirectionScale(){}, updateDrawableScale(){},
    updateDrawableVisible(){}, updateDrawableEffect(){}, updateDrawableOrder(){}, setLayerGroupOrdering(){}, getFencedPositionOfDrawable(id,pos){return pos;},
    penClear(){calls.clear++;}, penStamp(){calls.stamp++;}, penLine(){calls.line++;}, penPoint(){calls.point++;},
    updateBitmapSkin(){}, updateSVGSkin(){}, destroySkin(){}, draw(){}, resize(){}, setStageSize(){}, extractDrawableScreenSpace(){},
    getSkinSize(){return [10,10];}, getSkinRotationCenter(){return [5,5];}, getCurrentSkinSize(){return [10,10];},
    getBounds(){return {left:-5,right:5,top:5,bottom:-5};}, getBoundsForBubble(){return {left:-5,right:5,top:5,bottom:-5};},
    isTouchingDrawables(){return false;}, isTouchingColor(){return false;}, pick(){return -1;}, 
    getNativeSize(){return [480,360];}, createTextSkin(){return nextId++;}, updateTextSkin(){}, setDrawableOrder(){}, 
    _allDrawables:{}, offscreenTouching:false, markSkinAsDirty(){}, requestSnapshot(){}, 
  };
  
  const buf=fs.readFileSync(file);
  await vm.loadProject(buf);
  return {vm,calls};
}
module.exports=main;
if(require.main===module){
 main(process.argv[2]).then(async({vm,calls})=>{
  vm.start(); vm.greenFlag();
  await new Promise(r=>setTimeout(r,1500));
  vm.stop?.();
  const st=vm.runtime.getTargetForStage();
  for(const [id,v] of Object.entries(st.variables)) console.log(v.name,JSON.stringify(v.value).slice(0,200));
  console.log(calls);
  process.exit(0);
 }).catch(e=>{console.error('ERR',e);process.exit(1)});
}
