document.addEventListener('DOMContentLoaded', function() {
    // hide all exercise popdown divs
    document.querySelectorAll('.popdown').forEach(div => {
        div.style.display = "none"
    })
    // add click listener to all exercise title divs
    document.querySelectorAll('.fake-link').forEach(div => {
        div.onclick = showinfo
    })
})

function showinfo() {
    // hide/clear all other exercise data
    document.querySelectorAll('.popdown').forEach(div => {
        div.innerHTML = ""
        div.style.display = "none"
    })
    // get exercise pks from dataset
    let exercise = this.dataset.exercise;
    let popdown = document.querySelector(`#popdown-${exercise}`);
    fetch(`/progressAPI/${exercise}`)
    .then(response => response.json())
    .then(sets => {
        table = document.createElement('table')
        table.className = "table"
        table.innerHTML = `<thead class="thead-light"><tr>
                                <th scope="col">Date</th>
                                <th scope="col">Weight</th>
                                <th scope="col">Time</th>
                            </tr></thead>`
        sets.forEach(set => {
            row = document.createElement('tr')
            row.innerHTML = `
                                <td>${set.date}</td>
                                <td>${set.weight}</td>
                                <td>${set.time}</td>`
            table.append(row)
        })
        popdown.append(table)
        popdown.style.display = "block"
    })
}