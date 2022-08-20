const delete_btn = document.querySelector("#delete_btn");
delete_btn.addEventListener("click", (e) => {
  artist_id = delete_btn.dataset.artist_id;

  fetch(`/artist/${artist_id}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => {
      if (res.ok) {
        return Promise.resolve("Venue was deleted succesfully");
      } else {
        return Promise.reject("Error was occured an Venue deleted");
      }
    })
    .then((res) => window.location.replace("/artists"));
});
