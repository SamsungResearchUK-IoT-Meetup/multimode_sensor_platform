
// Progressive Enhancement (SW supported)
// if ('serviceWorker' in navigator) {
if (navigator.serviceWorker) {

  // Register the SW
  console.log('Attempting to register the service worker....')
  navigator.serviceWorker.register('/sw.js').then(function(registration){

    console.log('SW Registered');

  }).catch(function (error){
    console.log('Service Worker registration error');
    console.log(error);
  });

}
