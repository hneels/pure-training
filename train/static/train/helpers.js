// functions used in both newsession2.js and editsession2.js

// submit a Set to DB
function addset() {
    // Get form inputs from the set that was clicked
    let setnum = document.getElementById(`setnum-${this.dataset.setgroup}-${this.dataset.row}`).value
    let weight = document.getElementById(`weight-${this.dataset.setgroup}-${this.dataset.row}`).value
    let time = document.getElementById(`time-${this.dataset.setgroup}-${this.dataset.row}`).value
    if (validate(setnum) && validate(weight) && validate(time)) {
        // send info to API
        fetch('/postset', {
            method: 'POST',
            body: JSON.stringify({
                grouppk: this.dataset.setgroup,
                setnum: setnum,
                weight: weight,
                time: time,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                // if saved successfully, disable input fields
                document.getElementById(`weight-${this.dataset.setgroup}-${this.dataset.row}`).disabled = true
                document.getElementById(`time-${this.dataset.setgroup}-${this.dataset.row}`).disabled = true
                // update button class and display to EDIT
                this.className = "editset btn btn-sm btn-danger"
                this.innerHTML = "Edit"
                // add click listener to edit buttons
                document.querySelectorAll('.editset').forEach(btn => {
                    btn.onclick = editset
                    }
                )
            }
            // if set not saved successfully, display error msg alert
            else {
                alert(data.error)
            }
        })
    }
}

// edit a set that's already been submitted
function editset() {
    // enable input fields and change EDIT button so user can update set values
    document.getElementById(`weight-${this.dataset.setgroup}-${this.dataset.row}`).disabled = false
    document.getElementById(`time-${this.dataset.setgroup}-${this.dataset.row}`).disabled = false
    this.className = "addset btn btn-sm btn-outline-danger"
    this.innerHTML = "Save"
    // remove EDIT event listener
    this.onclick = null
    // add click listener to this SAVE button
    document.querySelectorAll('.addset').forEach(btn => {
        btn.onclick = addset
        })
}

// add or update a Note for a Setgroup
function setgroupinfo() {
    // text from note input
    let grouppk = this.dataset.setgroup
    let order = document.getElementById(`order-${grouppk}`).value
    let note = document.getElementById(`note-${grouppk}`).value
    
    // if note is not blank
    if (validate(order) && (validate(note))) {
        // send info to API
        fetch('/setgroupinfo', {
            method: 'PUT',
            body: JSON.stringify({
                grouppk: grouppk,
                order: order,
                note: note
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                // if saved successfully, disable fields
                document.getElementById(`order-${grouppk}`).disabled = true
                document.getElementById(`note-${grouppk}`).disabled = true
                // update button class and display to EDIT
                this.className = "editsetgroup btn btn-sm btn-danger"
                this.innerHTML = "Edit"
                // add click listener to edit buttons
                document.querySelectorAll('.editsetgroup').forEach(btn => {
                    btn.onclick = editsetgroupinfo
                    }
                )
            }
            // if note not saved successfully, display error msg alert
            else {
                alert(data.error)
            }
        })
    }
}

// edit setgroup info that's already been submitted
function editsetgroupinfo() {
    // enable input fields and change EDIT button so user can update setgroup values
    document.getElementById(`order-${this.dataset.setgroup}`).disabled = false
    document.getElementById(`note-${this.dataset.setgroup}`).disabled = false
    this.className = "setgroupinfo btn btn-sm btn-outline-danger"
    this.innerHTML = "Save"
    // remove EDIT event listener
    this.onclick = null
    // add click listener to this SAVE button
    document.querySelectorAll('.setgroupinfo').forEach(btn => {
        btn.onclick = setgroupinfo
        })
}

// Delete the whole session
function deletesession() {
    let sessionpk = this.dataset.sessionpk
    if(confirm("Delete this session? All previously entered sets will be deleted.")) {
        fetch(`/deletesession/${sessionpk}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                // if session deleted, return to home page
                window.location.href = '/'
            }
            // if note not saved successfully, display error msg alert
            else {
                alert(data.error)
            }
        })
    }
}

// prevent blank form inputs
function validate(input) {
    if (input == "") {
        alert('Missing Field');
        return false;
    }
    return true;
}

function appendrow() {
    const newrow = document.createElement('div');
    // get current row number and setgroup's pk from addset button data
    let numrows = parseInt(this.dataset.numrows);
    let grouppk = parseInt(this.dataset.grouppk);
    // update the number of rows here and in button data
    numrows = numrows + 1;
    this.dataset.numrows = numrows;
    newrow.innerHTML = `
                    <div class="form-row">
                        <div class="col-2">
                            <input id="setnum-${grouppk}-${numrows}" type="number" class="form-control form-control-sm" value="${numrows}" disabled>
                        </div>
                        <div class="col-4">
                            <input id="weight-${grouppk}-${numrows}" type="text" class="form-control form-control-sm" placeholder="Weight or Band">
                        </div>
                        <div class="col-4">
                            <input id="time-${grouppk}-${numrows}" type="text" class="form-control form-control-sm" placeholder="0 min 0 sec">
                        </div>
                        <div class="col">
                            <button data-setgroup="${grouppk}" data-row="${numrows}"
                            class="addset btn btn-sm btn-outline-danger">Save</button>
                        </div>
                    </div>
                    <hr>`
    // add new form row to the DOM
    document.getElementById(`xtrasets-${grouppk}`).append(newrow)
    // then add event listener to the new addset button
    document.querySelectorAll('.addset').forEach(btn => {
        btn.onclick = addset
        }
    )
}

function completesession() {
    let sessionpk = this.dataset.sessionpk
    // check if this session has any sets logged
    fetch(`/checkcomplete/${sessionpk}`)
    .then(response => response.json())
    .then(data => {
        // if sets have been logged for session
        if (data.message == 'has sets') {
            // if 0 empty setgroups: redirect to home page
            if (data.emptygroups == 0) {
                window.location.href = '/'
            }
            // if > 0 empty setgroups: confirm empty setgroups will be deleted
            else {
                if(confirm(`${data.emptygroups} empty exercise(s) will be deleted. This will not alter the routine.`)) {
                    // send API request: delete empty setgroups
                    fetch(`/deleteempties/${sessionpk}`, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if(data.message) {
                            // if empty setgroups successfully deleted, return to home page
                            window.location.href = '/'
                        }
                        else {
                            alert(data.error)
                        }
                    })
                }
            }
        }
        else if (data.message == 'no sets') {
            // if no sets -- confirm session will be deleted
            if(confirm("This session will be deleted because no sets have been logged")) {
                fetch(`/deletesession/${sessionpk}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // if session deleted, return to home page
                        window.location.href = '/'
                    }
                    // if session not deleted, display error msg alert
                    else {
                        alert(data.error)
                    }
                })
            }
        }
        else {
            alert(data.error)
        }
    })
}

function addexercise() {
    // pk of exercise to be added
    let exerciseid = this.value
    // pk of session
    let session = this.dataset.session
    // try to associate new exercise  with this session
    fetch('/anotherexercise', {
        method: 'POST',
        body: JSON.stringify({
            exerciseid: exerciseid,
            session: session
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.setgroup) {

            // if new setgroup successfully created: display
            let newdiv = document.createElement('div')
            // html for the Group name and note
            let string = `
            <div class="set-group">
                <div class="row">
                    <div class="col">
                        <h5>${data.name} Sets</h5>
                    </div>
                </div>
                <div class="form-row" id="row-${data.setgroup}">
                    <div class="col-2">
                        <input id="order-${data.setgroup}" type="text" class="form-control form-control-sm">
                    </div>
                    <div class="col-8">
                        <input id="note-${data.setgroup}" type="text" class="form-control form-control-sm" 
                                placeholder="Note: upper Kaatsu, lower Kaatsu, etc.">
                    </div>
                    <div class="col">
                        <button data-setgroup="${data.setgroup}" class="setgroupinfo btn btn-sm btn-outline-danger">Save</button>
                    </div>
                </div>
                `
            // html for each form row (need to SAVE value of i for numrows dataset below)
            let i = 1;
            for (i; i < 4; i++) {
                string = string + `
                <hr>
                <div class="form-row" id="row-${data.setgroup}-${i}">
                    <div class="col-2">
                        <input id="setnum-${data.setgroup}-${i}" type="number" class="form-control form-control-sm" value="${i}" disabled>
                    </div>
                    <div class="col-4">
                        <input id="weight-${data.setgroup}-${i}" type="text" class="form-control form-control-sm" placeholder="Weight or Band">
                    </div>
                    <div class="col-4">
                        <input id="time-${data.setgroup}-${i}" type="text" class="form-control form-control-sm" placeholder="0 min 0 sec">
                    </div>
                    <div class="col">
                        <button data-setgroup="${data.setgroup}" data-row="${i}"
                        class="addset btn btn-sm btn-outline-danger">Save</button>
                    </div>
                </div>
                `
            }
            // add extra sets section and close the div
            string = string + `
                <hr>
                <div id="xtrasets-${data.setgroup}"></div>
                <button data-numrows=${i} data-grouppk=${data.setgroup}
                class="appendrow float-right btn btn-sm btn-secondary">Add Another Set</button>
            </div>`
            // add HTML string to div
            newdiv.innerHTML = string
            document.querySelector('#moreexercises').append(newdiv)
        }
        else {
            // alert with error
            alert(data.error)
        }
    })
}

export {addset, editset, deletesession, completesession, validate, appendrow, setgroupinfo, addexercise}