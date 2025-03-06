const socket = new WebSocket("ws://127.0.0.1:8765");

// Initialize Leaflet Map
const map = L.map('map').setView([40.631021, -8.691643], 15); // Default center
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const MessageType = Object.freeze({
    PERCEPTION: 1,
    AWARENESS: 2
})

let activeObjects = []
let carMarkers = {};


socket.onopen = () => {
    console.log("Connected to WebSocket server");
};

socket.onmessage = (event) => {
    //console.log("Received from server:", event.data);

    try {
        const data = JSON.parse(event.data);

        // Extract position from both possible formats
        let lat, lon;

        if (data["dynamics"]){ 
            car_id = data["id"];
            lat = data.dynamics.properties.basicContainer.referencePosition.latitude / 1e7; 
            lon = data.dynamics.properties.basicContainer.referencePosition.longitude / 1e7;
            // TODO: Change AWARENESS TO OTHER, for different icon for the own DT?
            updateCarMarker(MessageType.AWARENESS, car_id, lat, lon);

        } else if (data["awareness"]) { 
            car_id = data["id"];
            lat = data.awareness.properties[car_id].latitude / 1e7; 
            lon = data.awareness.properties[car_id].longitude / 1e7;
            updateCarMarker(MessageType.AWARENESS, car_id, lat, lon);
            
        } else if (data["perception"]){
            for(const id in data.perception.properties){
                if (id === "generationDeltaTime") continue; //skip timestamp
                obj_id = id
                lat = data.perception.properties[obj_id].latitude;
                lon = data.perception.properties[obj_id].longitude;
                updateCarMarker(MessageType.PERCEPTION, obj_id, lat, lon)
            }
        }
            
    } catch (error) {
        console.error("Error parsing message:", error);
    }
};

socket.onclose = () => {
    console.log("WebSocket connection closed");
};

socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value;
    socket.send(message);
    input.value = "";
}

function updateCarMarker(markerMode, car_id, lat, lon) {

    if (markerMode == 1){
        if (carMarkers[car_id]) {
            carMarkers[car_id].setLatLng([lat, lon]); // Update position

        } else {
            let carIcon = L.divIcon({
                html: '<i class="fas fa-car" style="color: red; font-size: 18px;"></i>',
                className: 'custom-icon'
            });

            carMarkers[car_id] = L.marker([lat, lon], {icon: carIcon}).addTo(map)
                .bindPopup(`Car Position: ${lat}, ${lon}`);
        }

    }else if (markerMode == 2){

        if (carMarkers[car_id]) {
            carMarkers[car_id].setLatLng([lat, lon]); // Update position

        } else {
            let carIcon = L.divIcon({
                html: '<i class="fas fa-car" style="color: blue; font-size: 18px;"></i>',
                className: 'custom-icon'
            });

            carMarkers[car_id] = L.marker([lat, lon], {icon: carIcon}).addTo(map)
                .bindPopup(`Car Position: ${lat}, ${lon}`);
        }
    }else{}

}