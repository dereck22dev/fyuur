const delete_btn=document.querySelector('#delete_btn');
delete_btn.addEventListener('click',()=>{
    venue_id=delete_btn.dataset.venue_id;
    console.log(venue_id)

    fetch(`/venues/${venue_id}`, {
        method: 'DELETE', 
        headers: {
            'Content-Type': 'application/json'
        }}) .then(res => {
            if (res.ok && res.status==200) {
                return Promise.resolve('Venue was deleted succesfully');
            } else {
                return Promise.reject('Error was occured an Venue deleted');
            }
        })
        .then(res => window.location.replace('/venues')); 
})