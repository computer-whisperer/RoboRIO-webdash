

function netconsole_message(msg){
    $("#netconsole-data").append(msg.data.replace(/(?:\r\n|\r|\n)/g, '<br />'))
    $("#netconsole-block").prop("scrollTop", $("#netconsole-block").prop("scrollHeight") - $('#netconsole-block').height())
}

var netconsole = new WebSocket("ws:" + window.location.host + '/netconsole')

$(document).ready(function(){
   netconsole.onmessage = netconsole_message
})