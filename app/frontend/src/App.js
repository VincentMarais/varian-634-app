import React, { useState, useEffect } from 'react';
import useSocket from './hooks/useSocket';
import ScanningControlPanel from './components/ScanningControlPanel';
import ChartComponent from './components/ChartComponent';
import './App.css';

const App = () => {
  const socket = useSocket('http://127.0.0.1:5000');
  const [AbsorbanceData, setAbsorbanceData] = useState([]);

  useEffect(() => {
    if (socket) {
      socket.on('update_data', (data) => {
        setAbsorbanceData(prevData => [...prevData, data]);
      });
    }
  }, [socket]);




  


  const downloadCsv = () => {
    // Organisation des données par slitId
    const organizedData = AbsorbanceData.reduce((acc, data) => {
      if (!acc[data.slitId]) {
        acc[data.slitId] = [];
      }
      acc[data.slitId].push(data);
      return acc;
    }, {});
  
    // Préparation des en-têtes de colonnes pour chaque slitId
    // On suppose que tous les enregistrements pour un même slitId ont les mêmes longueurs d'onde (data_x)
    const headers = ['Longueur d\'onde (nm)', ...Object.keys(organizedData).map(slitId => `Absorbance (${slitId})`)];
    const csvRows = [headers.join(',')];
  
    // Construction des lignes de données
    const maxRows = Math.max(...Object.values(organizedData).map(data => data.length));
    for (let i = 0; i < maxRows; i++) {
      const row = [];
      row.push(AbsorbanceData[i]?.data_x ?? ''); // Ajoute la longueur d'onde si disponible
      Object.keys(organizedData).forEach(slitId => {
        const data = organizedData[slitId][i];
        row.push(data?.data_y ?? '');
      });
      csvRows.push(row.join(','));
    }
  
    // Conversion du tableau en une chaîne de caractères, chaque élément étant séparé par un saut de ligne
    const csvString = csvRows.join('\n');
    
    // Suite identique pour la création du blob, de l'URL et du déclenchement du téléchargement
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'data_VARIAN_634_grouped_by_slitId.csv'; // Nom du fichier adapté
    link.click();
  };
  
  const resetGraphData = () => {
    setAbsorbanceData([]);
  };

  return (
    <div className="App">
      <ChartComponent AbsorbanceData={AbsorbanceData} />
      <ScanningControlPanel
        socket={socket}
        downloadCsv={downloadCsv}
        resetGraphData={resetGraphData}
      />
    </div>
  );
};

export default App;