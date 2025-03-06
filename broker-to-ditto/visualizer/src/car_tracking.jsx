import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

const MessageType = {
    PERCEPTION: 1,
    AWARENESS: 2,
  };
  
const CarTracking = () => {
    const [carMarkers, setCarMarkers] = useState({});
    const socketUrl = "ws://127.0.0.1:8765";
  
    useEffect(() => {
      const newSocket = new WebSocket(socketUrl);
  
      newSocket.onopen = () => {
        console.log("Connected to WebSocket server");
      }
  
      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          setCarMarkers((prevMarkers) => {
            let newMarkers = { ...prevMarkers };
    
            if (data["dynamics"]) {
              const car_id = data["id"];
              const lat = data.dynamics.properties.basicContainer.referencePosition.latitude / 1e7;
              const lon = data.dynamics.properties.basicContainer.referencePosition.longitude / 1e7;
              newMarkers[car_id] = { lat, lon, type: MessageType.AWARENESS };
            } else if (data["awareness"]) {
              const car_id = data["id"];
              const lat = data.awareness.properties[car_id].latitude / 1e7;
              const lon = data.awareness.properties[car_id].longitude / 1e7;
              newMarkers[car_id] = { lat, lon, type: MessageType.AWARENESS };
            } else if (data["perception"]) {
              for (const id in data.perception.properties) {
                if (id === "generationDeltaTime") continue;
                newMarkers[id] = {
                  lat: data.perception.properties[id].latitude,
                  lon: data.perception.properties[id].longitude,
                  type: MessageType.PERCEPTION,
                };
              }
            }

            return newMarkers;
          });
        } catch (error) {
          console.error("Error parsing message:", error);
        }
      };
  
      newSocket.onclose = () => {
        console.log("WebSocket connection closed");
      }

      newSocket.onerror = (error) => console.error("WebSocket error:", error);

      return () => {
        if (newSocket.readyState === WebSocket.OPEN) {
          newSocket.close();
        }
      };
    }, []);

    const getCarIcon = (type) =>
      L.icon({
        iconUrl: type === MessageType.AWARENESS ? "/static/iconAzul.png" : "/static/iconVermelho.png",
        iconSize: [24, 24], 
        iconAnchor: [16, 16], 
        popupAnchor: [0, -16], 
      });

    return (
        <MapContainer center={[40.631021, -8.691643]} zoom={15} style={{ height: "100vh", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
            {Object.entries(carMarkers).map(([id, { lat, lon, type }]) => (
            <Marker key={id} position={[lat, lon]} icon={getCarIcon(type)}>
                <Popup>Car Position: {lat}, {lon}</Popup>
            </Marker>
            ))}
        </MapContainer>
        );
    };

export default CarTracking;