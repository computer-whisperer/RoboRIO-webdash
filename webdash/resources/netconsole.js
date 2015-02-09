var netconsole
var connected = false
var first_connect = true

function start_netconsole(){
    netconsole = new WebSocket("ws:" + window.location.host + '/netconsole')
    netconsole.onmessage = netconsole_message
    netconsole.onopen = netconsole_connect
    netconsole.onclose = netconsole_close
    netconsole.onerror = netconsole_error
}

function netconsole_connect(e){
    netconsole_clear()
    setBadge("#netconsole-status", true, "Connected")
    if(!first_connect){
        netconsole_print_colored("Reconnected to Server", "green")
    }
    connected = true
    first_connect = false
}

function netconsole_error(e){
    console.log("netconsole_error")
}

function netconsole_close(e){
    if(connected){
        netconsole_print_colored("Lost Connection with Server", "red")
        connected = false
        setBadge("#netconsole-status", false, "Disconnected")
    }
    setTimeout(start_netconsole, 1000)
}

function netconsole_print_colored(msg, color){
    netconsole_print("<span class='netconsole-status-" + color + "'>WebDash: " + msg + "</span><br/>")
}

function netconsole_message(e){
    netconsole_print(e.data)
}

function netconsole_print(msg){
    $("#netconsole-data").append(msg.replace(/(?:\r\n|\r|\n)/g, '<br />'))
    $("#netconsole-block").prop("scrollTop", $("#netconsole-block").prop("scrollHeight") - $('#netconsole-block').height())
}

function netconsole_clear(){
    $("#netconsole-data").text("")
}

$(document).ready(function(){
   start_netconsole()
})