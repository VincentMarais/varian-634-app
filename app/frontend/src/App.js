import React, { useState, useEffect } from 'react';
import useSocket from './hooks/useSocket';
import SensorControlPanel from './components/SensorControlPanel';
import ChartComponent from './components/ChartComponent';
import './App.css';

const App = () => {
  const socket = useSocket('http://127.0.0.1:5000');
  const [temperatureData, setTemperatureData] = useState([]);
  const [isGeneratingData, setIsGeneratingData] = useState(false);

  useEffect(() => {
    if (socket) {
      socket.on('updateSensorData', (data) => {
        setTemperatureData(prevData => [...prevData, data]);
      });
    }
  }, [socket]);

  const toggleSocketConnection = () => {
    if (socket.connected) {
      socket.disconnect();
    } else {
      socket.connect();
    }
  };

  // Dans votre composant React
  const toggleDataGeneration = () => {
    if (isGeneratingData) {
      socket.emit('stopSensorData');  // Envoie l'événement pour arrêter la génération des données
    } else {
      socket.emit('startSensorData'); // Envoie l'événement pour démarrer la génération des données
    }
    setIsGeneratingData(!isGeneratingData); // Inverse l'état pour refléter le changement
  };

  


  const downloadCsv = () => {
    const csvRows = ['date,value', ...temperatureData.map(d => `${d.date},${d.value}`)];
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'temperature_data.csv';
    link.click();
  };

  const resetGraphData = () => {
    setTemperatureData([]);
  };

  return (
    <div className="App">
      <ChartComponent temperatureData={temperatureData} />
      <SensorControlPanel
        socket={socket}
        isGeneratingData={isGeneratingData}
        toggleSocketConnection={toggleSocketConnection}
        startSensorDataGeneration={toggleDataGeneration} // Ici, vous passez la fonction comme prop
        downloadCsv={downloadCsv}
        resetGraphData={resetGraphData}
      />
    </div>
  );
};

export default App;
