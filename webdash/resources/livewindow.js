var livewindow_enabled = false

function start_livewindow(){
    update_livewindow()
}

function update_livewindow(){

    if (networktables_connected && networktables_data["LiveWindow"]["~STATUS~"]["LW Enabled"]){
        enable_livewindow()
    }
    else{
        disable_livewindow()
    }

    if (livewindow_enabled){
        livewindow_data = networktables_data["LiveWindow"]
        devices = []
        for (section in livewindow_data){
            devices.concat(get_devices(livewindow_data[section]))
        }
    }
    setTimeout(update_livewindow, 500);
}

function get_devices(livewindow_object){
    devices = []
    for (i in livewindow_object){
        if (i.lastIndexOf("~", 0) == 0){
            continue;
        }
        if (livewindow_object[i]["~TYPE~"] == "LW Subsystem"){
            new_devices = get_devices(livewindow_object[i])
            devices.concat(new_devices)
        }
        else{
            devices.push(livewindow_object[i])
        }
    }
}

function enable_livewindow(){
    if (livewindow_enabled){
        return
    }
    $("#livewindow-status").text("Enabled")
    $("#livewindow-status").removeClass("label-danger")
    $("#livewindow-status").addClass("label-success")
    $("#livewindow-devices").addClass("livewindow-enabled")
    $("#livewindow-devices").removeClass("livewindow-disabled")
    livewindow_enabled = true
}

function disable_livewindow(){
    if (!livewindow_enabled){
        return
    }
    $("#livewindow-status").text("Disabled")
    $("#livewindow-status").addClass("label-danger")
    $("#livewindow-status").removeClass("label-success")
    $("#livewindow-devices").removeClass("livewindow-enabled")
    $("#livewindow-devices").addClass("livewindow-disabled")
    livewindow_enabled = false
}

$(document).ready(function(){
   start_livewindow()
})