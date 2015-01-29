var networktables_websocket
var networktables_connected = false

function start_networktables(){
    networktables_websocket = new WebSocket("ws:" + window.location.host + '/networktables')
    networktables_websocket.onmessage = networktables_message
    networktables_websocket.onopen = networktables_connect
    networktables_websocket.onclose = networktables_close
    networktables_websocket.onerror = networktables_error
    networktables_set_table()
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

var root_table = ""

var networktables_data = []

function networktables_message(e){
    obj = JSON.parse(e.data)
    update_object(networktables_data, obj)
    update_networktables_ui()
}

function networktables_set_table(){
    root_table = $("#networktables-select").val()
    update_networktables_ui()
}

function update_object(tgt, src){
    for (var key in src){
        if (typeof obj[key] == "object"){
            if (!tgt.hasOwnProperty(key)){
                tgt[key] = []
            }
            update_object(tgt[key], src[key])
        }
        else{
            tgt[key] = src[key]
        }
    }
}

function flatten_object(obj){
    var result = []
    for (var key in obj){
        if (typeof obj[key] == "object"){
            var subflat = flatten_object(obj[key])
            for (s in subflat){
                result["/" + key + s] = subflat[s]
            }
        }
        else{
            result["/" + key] = obj[key]
        }
    }
    return result
}

function update_networktables_ui(){
    //Clear UI
    $("#networktables-table tbody tr").remove()

    //Flatten data
    flattened_data = flatten_object(networktables_data)

    //Filter table
    filtered_data = []
    for (i in flattened_data){
        if (i.lastIndexOf(root_table, 0) == 0){
            newname = i.replace(root_table, "")
            filtered_data[newname] = flattened_data[i]
        }
    }

    //Sort table
    table_order = []
    for (i in filtered_data){
        table_order.push(i)
    }
    table_order.sort()

    //Generate HTML
    html = ""
    for (i=0; i < table_order.length; i++){
        name = table_order[i]
        html += '<tr><td>' + name +
                '</td><td>' + filtered_data[name] + '</td></tr>';
    }
    $("#networktables-table tbody").html(html)
}

$(document).ready(function(){
   start_networktables()
})