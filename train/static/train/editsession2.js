import {deletesession, completesession, validate, appendrow, setgroupinfo, addexercise} from './helpers.js';

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.setgroupinfo').forEach(btn => {
        btn.onclick = setgroupinfo
    })
    document.querySelectorAll('.updateset').forEach(btn => {
        btn.onclick = updateset
    })
    document.querySelectorAll('.appendrow').forEach(btn => {
        btn.onclick = appendrow
    })
    
    document.querySelector('.delete').onclick = deletesession;
    document.querySelector('.finish').onclick = completesession;

    // setup for Add Exercise div
    const dropdowndiv = document.querySelector('#dropdowndiv')
    dropdowndiv.style.display = 'none';
    const showdivbtn = document.querySelector('#showdiv')
    showdivbtn.addEventListener('click', () => {
        dropdowndiv.style.display = 'block'
        showdivbtn.style.display = 'none'
    })
    // Add Exercise select list
    document.querySelector('#exercise-select').onchange = addexercise
})

function updateset() {
    let setpk = this.dataset.setpk
    let weight = document.getElementById(`weight-${setpk}`).value
    let time = document.getElementById(`time-${setpk}`).value

    if (validate(weight) && validate(time)) {
        // send PUT request with set pk, weight, and time
        fetch('/updateset', {
            method: 'PUT',
            body: JSON.stringify({
                setpk: setpk,
                weight: weight,
                time: time
            })
        })
        .then(response => response.json())
        .then(data => {
            // if set was successfully updated, disable input fields
            if (data.message) {
                document.getElementById(`weight-${setpk}`).disabled = true
                document.getElementById(`time-${setpk}`).disabled = true
            }
            // if set not saved successfully, display error msg alert
            else {
                alert(data.error)
            }
        })
    }
}

