import './app.css';
import CarTracking from './car_tracking';

function app() {
  return (
    <div>
      <div id = "title-bar">
        <h2>Digital Twin Visualizer</h2>
      </div>
      <CarTracking/>
    </div>

    
  );
}

export default app;
