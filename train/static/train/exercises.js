document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll(".delete").forEach(button => {
        button.onclick = deleteclick;
    });
})


function deleteclick() {
    // delete an exercise and hide the exercise row
    exercise = this.dataset.exercise
    row = document.getElementById(`row-${exercise}`)

    fetch('/deletex', {
        method: 'DELETE',
        body: JSON.stringify({
            exercise: exercise
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // if exercise deleted successfully, hide row
            row.style.display = "none"
        }
        else {
            alert(data.message)
        }
    })



    
}