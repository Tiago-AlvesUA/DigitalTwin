import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Circle, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

const MessageType = {
    PERCEPTION: 1,
    AWARENESS: 2,
    TRAJECTORY: 3
  };
  
const CarTracking = () => {
    const [carMarkers, setCarMarkers] = useState({});
    const [carTrajectories, setCarTrajectories] = useState({});
    const socketUrl = "ws://127.0.0.1:8765";
  
    useEffect(() => {
      const newSocket = new WebSocket(socketUrl);
  
      newSocket.onopen = () => {
        console.log("Connected to WebSocket server");
      }
  
      newSocket.onmessage = (event) => {
        // console.log("Received message:", event.data);

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

          setCarTrajectories((prevTrajectories) => {
            let newTrajectories = { ...prevTrajectories };
  
            if (data["receiverTrajectory"]) {

              const car_id = data["id"];
              //console.log(data)

              const newTrajectory = data.receiverTrajectory.map(({ latitude, longitude }) => ({
                lat: latitude/1e7,
                lon: longitude/1e7,
                type: "receiver",
              }));

              let dummy_car_id = car_id + 1; // TODO: remove and leave car_id as normal
              newTrajectories[dummy_car_id] = newTrajectory; 

            } else if (data["senderTrajectory"]) {
              //console.log(data)
              const car_id = data["id"];
              const newTrajectory = data.senderTrajectory.properties[car_id].map(({ latitude, longitude }) => ({
                lat: latitude / 1e7,
                lon: longitude / 1e7,
                type: "sender",
              }));
              //console.log("Trajectory:", newTrajectory);
              newTrajectories[car_id] = newTrajectory;
            }

            else if (data["senderInterpolatedPoints"]) {
              const car_id = data["id"];
              const newTrajectory = data.senderInterpolatedPoints.map(({ latitude, longitude }) => ({
                lat: latitude / 1e7,
                lon: longitude / 1e7,
                type: "senderInterp",
              }));

              newTrajectories[car_id] = newTrajectory;
            }

            else if (data["receiverInterpolatedPoints"]) {
              const car_id = data["id"];
              const newTrajectory = data.receiverInterpolatedPoints.map(({ latitude, longitude }) => ({
                lat: latitude / 1e7,
                lon: longitude / 1e7,
                type: "receiverInterp",
              }));

              newTrajectories[car_id] = newTrajectory;
            }

            return newTrajectories;
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
        iconSize: [16, 16], 
        iconAnchor: [16, 16], 
        popupAnchor: [0, -16], 
      });

    return (
        <MapContainer center={[40.631021, -8.691643]} zoom={18} style={{ height: "100vh", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
            
            

            {Object.entries(carTrajectories).map(([id, trajectory]) => {
              // console.log(`Rendering trajectory for car ${id}`);
              return trajectory.map(({ lat, lon, type }, index) => {
                  let circleColor
                  //const circleColor = type === "receiver" ? "red" : "blue";
                  if (type === "receiver"){
                    circleColor = "red";
                  } else if (type === "sender"){
                    circleColor = "blue";
                  } else if (type === "senderInterp"){
                    circleColor = "#ADD8E6";
                  } else if (type === "receiverInterp"){
                    circleColor = "#FFA07A";
                  }
                  // console.log(`Rendering circle at ${lat}, ${lon}`);
                  return (
                      <Circle
                          key={`${id}-${index}`}
                          center={[lat, lon]}
                          radius={1}
                          pathOptions={{ color: circleColor, fillOpacity: 0.5 }}
                      />
                  );
              });
            })}

            {Object.entries(carMarkers).map(([id, { lat, lon, type }]) => (
              <Marker key={id} position={[lat, lon]} icon={getCarIcon(type)}>
                  <Popup>Car Position: {lat}, {lon}</Popup>
              </Marker>
            ))}
        </MapContainer>
        );
    };

export default CarTracking;


