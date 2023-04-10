// create a Leaflet map
var map = L.map('map').setView([45.5236, -122.6750], 10);
console.log('Map initiated');

// create a new marker layer group
var markerLayer = L.layerGroup().addTo(map);
console.log('create a new marker layer group');

// add an initial set of markers to the map
$.getJSON('/get_markers', {lat: 45.5236, lon: -122.6750, zoom: 10}, function(data) {
    for (var i = 0; i < data.length; i++) {
        var marker = L.marker(data[i]).addTo(markerLayer);
    }
});
console.log('add an initial set of markers to the map');

// create a function to update the markers when the map is moved or zoomed
function updateMarkers() {
    // get the current center and zoom level of the map
    var latlng = map.getCenter();
    var zoom = map.getZoom();
    console.log('get the current center and zoom level of the map');

    // send a GET request to the server to get the new markers
    $.getJSON('/get_markers', {lat: latlng.lat, lon: latlng.lng, zoom: zoom}, function(data) {
        // remove the old markers from the marker layer
        markerLayer.clearLayers();

        // add the new markers to the marker layer
        for (var i = 0; i < data.length; i++) {
            var marker = L.marker(data[i]).addTo(markerLayer);
        }
        console.log('send a GET request to the server to get the new markers');

    });
}

// call the updateMarkers function whenever the map is moved or zoomed
map.on('moveend', updateMarkers);
console.log('call the updateMarkers function whenever the map is moved or zoomed');

