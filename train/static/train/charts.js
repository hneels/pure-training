// Submit the Client form whenever selected, without submit button
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('client-select').addEventListener('change', ()=> {
        document.getElementById('select-form').submit()
    })
})