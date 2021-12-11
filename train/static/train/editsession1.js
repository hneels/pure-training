document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('session-form').style.display = "none";
    document.getElementById('client-select').addEventListener('change', changehandle);
})

function changehandle() {
    // submit selected client pk to server to retrieve this client's sessions
    client = this.value
    sessionselect = document.getElementById('session-select')
    fetch(`/fetchsessions/${client}`)
    .then(response => response.json())
    .then(sessions => {

        sessions.forEach(session => {
            // append a Select Option for each session
            const newoption = document.createElement('option')
            newoption.innerHTML = `${session.client}'s ${session.routine} on ${session.timestamp} - trained by ${session.trainer}`
            newoption.value = session.pk
            sessionselect.append(newoption)
        })
    })
    document.getElementById('session-form').style.display = "block";
}