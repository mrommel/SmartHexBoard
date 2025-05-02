export function handleError(xhr, textStatus, exception) {

    if (xhr.status === 0) {
        console.log('Not connect.\n Verify Network.');
    } else if (xhr.status === 404) {
        // 404 page error
        console.log('Requested page not found. [404]');
    } else if (xhr.status === 500) {
        // 500 Internal Server error
        console.log('Internal Server Error [500].');
    } else if (exception === 'parsererror') {
        // Requested JSON parse
        console.log('Requested JSON parse failed.');
    } else if (exception === 'timeout') {
        // Time out error
        console.log('Time out error.');
    } else if (exception === 'abort') {
        // request aborted
        console.log('Ajax request aborted.');
    } else {
        console.log('Uncaught Error.\n' + xhr.responseText);
    }
}