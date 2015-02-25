var livewindow_enabled = false

function start_livewindow(){
    update_livewindow()
}


function update_livewindow(){
    if (networktables_nt_connected && networktables_get_value("/LiveWindow/~STATUS~/LW Enabled")){
        enable_livewindow()
        next_sleep = 100
    }
    else{
        disable_livewindow()
        next_sleep = 500
    }

    if (livewindow_enabled){
        livewindow_data = networktables_data["LiveWindow"]
        new_html = ""
        for (section in livewindow_data){
            if (section.lastIndexOf("~", 0) == 0){
                continue
            }
            new_html += render_livewindow_object(livewindow_data[section])
        }
        $("#livewindow-devices").html(new_html)
    }

    setTimeout(update_livewindow, next_sleep);
}

function render_livewindow_object(obj){
    if (! obj.hasOwnProperty("~TYPE~")) return
    var type = obj["~TYPE~"]
    if (type == "LW Subsystem") return render_livewindow_subsystem(obj)
    else if (type == "Digital Input") return render_livewindow_digital_input(obj)
    else if (type == "Quadrature Encoder") return render_livewindow_encoder(obj)
    else if (type == "Speed Controller") return render_livewindow_speed_controller(obj)
    else if (type == "Analog Input") return render_livewindow_analog_input(obj)
    else if (type == "Gyro") return render_livewindow_gyro(obj)
    else return render_livewindow_generic(obj)
}

function render_livewindow_subsystem(obj){
    var html = ""
    for (i in obj){
        if (i.lastIndexOf("~", 0) != 0){
            html += render_livewindow_object(obj[i])
        }
    }
    return html
}

var livewindow_dev_html = " \
<div class='panel lw-dev-panel'>\
    <div class='panel-heading'>\
        <h2 class='panel-title'><span class='lw-dev-name'></span></h2>\
    </div>\
    <div class='panel-body'>\
        <div class='lw-dev-content'></div>\
    </div>\
</div>\
"

function render_livewindow_generic(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-primary")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    for (i in obj){
        jq_obj.find(".lw-dev-content").append("<br/>" + i + " = " + obj[i])
    }
    return $("<p/>").append(jq_obj).html()
}

function render_livewindow_digital_input(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-success")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    var html = "<h4>Value:  "
    if (obj["value"]){
        html += "<span class='label label-success'>True</span>"
    }
    else{
        html += "<span class='label label-danger'>False</span>"
    }
    html += "</h4>"
    jq_obj.find(".lw-dev-content").append(html)
    return $("<p/>").append(jq_obj).html()
}

function render_livewindow_encoder(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-warning")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    content = jq_obj.find(".lw-dev-content")
    content.append("<h4>Distance: " + obj["Distance"] + "</h4>")
    content.append("<h4>Distance per Tick: " + obj["Distance per Tick"] + "</h4>")
    content.append("<h4>Speed: " + obj["Speed"] + "</h4>")
    return $("<p/>").append(jq_obj).html()
}

function render_livewindow_speed_controller(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-info")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    content = jq_obj.find(".lw-dev-content")
    content.append("<h4>Value: " + obj["Value"] + "</h4>")
    return $("<p/>").append(jq_obj).html()
}

function render_livewindow_analog_input(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-default")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    content = jq_obj.find(".lw-dev-content")
    content.append("<h4>Value: " + obj["Value"] + "</h4>")
    return $("<p/>").append(jq_obj).html()
}

function render_livewindow_gyro(obj){
    jq_obj = $(livewindow_dev_html)
    jq_obj.addClass("panel-success")
    jq_obj.find(".lw-dev-name").html(obj["Name"])
    content = jq_obj.find(".lw-dev-content")
    content.append("<h4>Value: " + obj["Value"] + "</h4>")
    return $("<p/>").append(jq_obj).html()
}

function enable_livewindow(){
    if (livewindow_enabled){
        return
    }
    setBadge("#livewindow-status", true, "Enabled")
    $("#livewindow-devices").addClass("livewindow-enabled")
    $("#livewindow-devices").removeClass("livewindow-disabled")
    livewindow_enabled = true
}

function disable_livewindow(){
    if (!livewindow_enabled){
        return
    }
    setBadge("#livewindow-status", false, "Disabled")
    $("#livewindow-devices").removeClass("livewindow-enabled")
    $("#livewindow-devices").addClass("livewindow-disabled")
    livewindow_enabled = false
}

$(document).ready(function(){
   start_livewindow()
})