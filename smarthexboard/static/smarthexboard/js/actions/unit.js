import {handleError} from "../errorHandling.js";

export function unitActions(unit, game_uuid, callback) {
    const formData = new FormData();
    formData.append('location', unit.location.toString());
    formData.append('unit_type', unit.unitType.name);
    formData.append('player', unit.player.toString());
    formData.append('game_uuid', game_uuid);

    const csrf_token = $('#csrf_token').text();

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/game/actions",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            console.log('update game: ' + JSON.stringify(json_obj));
            callback(unit, json_obj['action_list']);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
            callback([]);
        }
    });
}