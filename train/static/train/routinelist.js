document.addEventListener('DOMContentLoaded', function() {
    // make all archived rows dark gray
    document.querySelectorAll('input[type=checkbox]:checked').forEach(box => {
        box.parentNode.parentNode.style.backgroundColor = "#E0E0E0"
    })

    document.querySelectorAll('tr').forEach(row => {
        row.onclick = goToForm
    })
    document.querySelectorAll('.check').forEach(box => {
        box.addEventListener('click', click => {
            archive(click)
        })
    })
})

function goToForm() {
    pk = this.id
    window.location.href = `/routines/edit/${pk}`
}

function archive(event) {
    event.stopPropagation()
    routine = event.target.dataset.routine

    fetch(`/archive/${routine}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then(data => {
        // if routine archived/unarchived
        if (data.message) {
            if (data.message == 'Routine archived') {
                // make row background darker
                event.target.parentNode.parentNode.style.backgroundColor = "#E0E0E0";
            } else {
                // make background normal
                event.target.parentNode.parentNode.style.backgroundColor = "#F5F5F5";
            }
        }
        else {
            alert(data.error)
        }
    })
}