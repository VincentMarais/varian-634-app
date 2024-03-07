import React, { useState } from 'react';

const SensorControlPanel = ({ socket,
  isGeneratingData,
  toggleSocketConnection,
  startSensorDataGeneration,
  downloadCsv,
  resetGraphData, }) => {
  const [wavelengthMin, setWavelengthMin] = useState('');
  const [wavelengthMax, setWavelengthMax] = useState('');
  const [step, setStep] = useState('');
  const [selectedCuvette, setSelectedCuvette] = useState('');
  const [selectedSlits, setSelectedSlits] = useState([]);

  // Cette fonction est maintenant ajustée pour envoyer les paramètres et démarrer la génération des données
  const startSensorData = () => {
    // Vérifiez si tous les paramètres nécessaires sont définis
    if (!wavelengthMin || !wavelengthMax || !step || !selectedCuvette || selectedSlits.length === 0) {
      alert("Veuillez remplir tous les champs avant de démarrer.");
      return;
    }
    // Envoyez les paramètres au serveur
    socket.emit('setScanningParams', { wavelengthMin, wavelengthMax, step, selectedCuvette, selectedSlits });
    // Demandez au serveur de démarrer la génération des données
    socket.emit('startSensorData');
  };

  const handleSlitChange = (slitValue) => {
    setSelectedSlits(prev => {
      if (prev.includes(slitValue)) {
        return prev.filter(slit => slit !== slitValue);
      } else {
        return [...prev, slitValue];
      }
    });
  };

  return (
    <div className="control-panel">
      <input
  type="number"
  value={wavelengthMin}
  onChange={(e) => setWavelengthMin(e.target.value)}
  style={{ marginBottom: '10px' }} // adjust the value to your desired margin size
  placeholder="Longueur d'onde Min [1,799]"
/>
      <input type="number" value={wavelengthMax} onChange={(e) => setWavelengthMax(e.target.value)} placeholder="Longueur d'onde Max [2,800]" />
      <input type="number" value={step} onChange={(e) => setStep(e.target.value)} placeholder="Étape [1,800]" />
      <div>
        <input type="radio" name="cuvette" value="cuvette 1" onChange={(e) => setSelectedCuvette(e.target.value)} /> Cuvette 1
        <input type="radio" name="cuvette" value="cuvette 2" onChange={(e) => setSelectedCuvette(e.target.value)} /> Cuvette 2
      </div>
      <div>
        <input type="checkbox" value="2nm" onChange={() => handleSlitChange('Fente_2nm')} /> Fente 2nm
        <input type="checkbox" value="1nm" onChange={() => handleSlitChange('Fente_1nm')} /> Fente 1nm
        <input type="checkbox" value="0.5nm" onChange={() => handleSlitChange('Fente_0_5nm')} /> Fente 0.5nm
        <input type="checkbox" value="0.2nm" onChange={() => handleSlitChange('Fente_0_2nm')} /> Fente 0.2nm
      </div>
      <button onClick={startSensorData}>
        Démarrer les données du capteur
      </button>
      <button onClick={downloadCsv}>Télécharger CSV</button>
      <button onClick={resetGraphData}>Réinitialiser les données du graphique</button>
    </div>
  );
};

export default SensorControlPanel;
