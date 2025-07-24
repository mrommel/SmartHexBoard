import {handleError} from "../errorHandling.js";
import { CityInfo } from "../map/city.js";

export function cityInfoAt(location, game_id, callback) {
    const formData = new FormData();
    formData.append('location', location);
    formData.append('game_id', game_id);

    const csrf_token = $('#csrf_token').text();

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/city_info",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            console.log('city info: ' + JSON.stringify(json_obj));
            let city_info = new CityInfo();
            city_info.fromJson(json_obj['info']);
            callback(city_info);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
            callback(null);
        }
    });
}
