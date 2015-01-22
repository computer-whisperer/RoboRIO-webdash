var networktables_websocket
var networktables_connected = false

function start_networktables(){
    networktables_websocket = new WebSocket("ws:" + window.location.host + '/networktables')
    networktables_websocket.onmessage = networktables_message
    networktables_websocket.onopen = networktables_connect
    networktables_websocket.onclose = networktables_close
    networktables_websocket.onerror = networktables_error
}

function networktables_connect(e){
    $("#networktables-status").text("Connected")
    $("#networktables-status").removeClass("label-danger")
    $("#networktables-status").addClass("label-success")
    networktables_connected = true
}

function networktables_error(e){
    console.log("networktables_error")
}

function networktables_close(e){
    if(networktables_connected){
        networktables_connected = false
        $("#networktables-status").text("Disconnected")
        $("#networktables-status").removeClass("label-success")
        $("#networktables-status").addClass("label-danger")
    }
    setTimeout(start_networktables, 1000)
}

var networktables_data = []

function networktables_message(e){
    obj = JSON.parse(e.data)
    for (i in obj){
        networktables_data[i] = obj[i]
    }
    update_networktables_ui()
}

function update_networktables_ui(){
    $("#networktables-table tbody tr").remove()
    table_order = []
    for (i in networktables_data){
        table_order.push(i)
    }
    table_order.sort()
    html = ""
    for (i=0; i < table_order.length; i++){
        name = table_order[i]
        html += '<tr><td>' + name +
                '</td><td>' + networktables_data[name] + '</td></tr>';
    }
    $("#networktables-table tbody").html(html)
}

$(document).ready(function(){
   start_networktables()
})