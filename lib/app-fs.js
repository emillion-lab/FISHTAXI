/* Цял екран: ред в менюто (работи в Chrome/Android; в iOS Safari няма такова API) */
(function(){
var de=document.documentElement,mb=document.getElementById('mbody');
if(!mb||!de.requestFullscreen)return;
function add(){
  if(mb.querySelector('[data-fs]'))return;
  var bg=de.lang!=='en';
  var d=document.createElement('div');d.className='pgrp';
  d.innerHTML='<a class="mrow" href="#" data-fs="1">'+(bg?'Цял екран':'Full screen')+'<small>›</small></a>';
  mb.insertBefore(d,mb.querySelector('.note'));
}
new MutationObserver(add).observe(mb,{childList:true});
mb.addEventListener('click',function(e){
  if(!e.target.closest('[data-fs]'))return;e.preventDefault();
  try{document.fullscreenElement?document.exitFullscreen():de.requestFullscreen({navigationUI:'hide'});}catch(er){}
});
})();
