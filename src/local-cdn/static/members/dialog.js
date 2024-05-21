const modal = new bootstrap.Modal(document.getElementById('modal'))

htmx.on('htmx:afterSwap', (event) => {
  // Response targeting #dialog => show the modalif
  if (event.detail.target.id == "dialog") {modal.show()
  }
})

htmx.on('htmx.beforeSwap', (event) => {
// Empty response targeting #dialog => hide the modal
if (event.detail.target.id == "dialog" && !e.detail.xhr.response) {
modal.hide()
e.detail.shouldSwap = false
  }
})

htmx.on("hidden.bs.modal", () => {
  document.getElementById("dialog").innerHTML = ""
})
