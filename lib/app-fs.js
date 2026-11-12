/* fish.taxi — цял екран без лентата на телефона (Android/Chrome).
 * Включен по подразбиране: браузърът позволява цял екран само след докосване,
 * затова се включва при първото докосване. В менюто: „Цял екран: вкл./изкл.“
 * В iOS Safari няма такова API — там редът не се показва.
 */
(function(){
var de=document.documentElement,mb=document.getElementById('mbody'),KEY='ft_fs';
if(!de.requestFullscreen)return;
function want(){try{return localStorage.getItem(KEY)!=='off';}catch(e){return true;}}
function on(){return !!document.fullscreenElement;}
function go(){if(on())return;try{var p=de.requestFullscreen({navigationUI:'hide'});if(p&&p.catch)p.catch(function(){});}catch(e){}}
/* при всяко докосване, ако е включено и в момента не сме на цял екран (напр. след „Назад“) */
document.addEventListener('pointerup',function(){if(want())go();},true);
function bg(){return de.lang!=='en';}
function label(){return (bg()?'Цял екран: ':'Full screen: ')+(want()?(bg()?'вкл.':'on'):(bg()?'изкл.':'off'));}
function add(){
  if(!mb||mb.querySelector('[data-fs]'))return;
  var d=document.createElement('div');d.className='pgrp';
  d.innerHTML='<a class="mrow" href="#" data-fs="1"><span>'+label()+'</span><small>'+(bg()?'скрива лентата горе':'hides the top bar')+'</small></a>';
  mb.insertBefore(d,mb.querySelector('.note'));
}
if(mb){
  new MutationObserver(add).observe(mb,{childList:true});
  mb.addEventListener('click',function(e){
    var a=e.target.closest('[data-fs]');if(!a)return;e.preventDefault();
    var w=!want();try{localStorage.setItem(KEY,w?'on':'off');}catch(er){}
    if(w)go();else if(on())document.exitFullscreen().catch(function(){});
    a.querySelector('span').textContent=label();
  });
}
})();
