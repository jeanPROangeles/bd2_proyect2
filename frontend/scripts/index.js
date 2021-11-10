document.getElementById('form').onsubmit = function(e){
    e.preventDefault();
    const query = document.getElementById('query');
    fetch('/score/'+query ,{    
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json'
        }
    })
    .then(function(){
        console.log('event: ', e);
    });
}

