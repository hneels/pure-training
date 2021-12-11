import {addset, appendrow, setgroupinfo, deletesession, completesession, addexercise} from './helpers.js';

document.addEventListener('DOMContentLoaded', function() {
    // setup for Add Exercise div
    const dropdowndiv = document.querySelector('#dropdowndiv')
    dropdowndiv.style.display = 'none';
    const showdivbtn = document.querySelector('#showdiv')
    showdivbtn.addEventListener('click', () => {
        dropdowndiv.style.display = 'block';
        showdivbtn.style.display = 'none';
    })
    // Add Exercise select list
    document.querySelector('#exercise-select').onchange = addexercise

    // addset button
    document.querySelectorAll('.addset').forEach(btn => {
        btn.onclick = addset
        }
    )
    // Add Setgroup order and note button
    document.querySelectorAll('.setgroupinfo').forEach(btn => {
        btn.onclick = setgroupinfo
    })
    // append a new Set row
    document.querySelectorAll('.appendrow').forEach(btn => {
        btn.onclick = appendrow
    })
    // delete and complete buttons at bottom
    document.querySelector('.delete').onclick = deletesession;
    document.querySelector('.finish').onclick = completesession;
})
