import React, { useState } from 'react';

const ScanningControlPanel = ({
  socket,
  downloadCsv,
  resetGraphData,
}) => {
  const [wavelengthMin, setWavelengthMin] = useState('');
  const [wavelengthMax, setWavelengthMax] = useState('');
  const [step, setStep] = useState('');
  const [selectedCuvette, setSelectedCuvette] = useState('');
  const [selectedSlits, setSelectedSlits] = useState([]);
  const [sampleName, setSampleName] = useState('');
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);

  const toggleSensorData = () => {
    if (!isSimulationRunning) {
      if (!wavelengthMin || !wavelengthMax || !step || !selectedCuvette || selectedSlits.length === 0 || !sampleName.trim()) {
        alert("Veuillez remplir tous les champs avant de démarrer.");
        return;
      }
      socket.emit('setScanningParams', { wavelengthMin, wavelengthMax, step, selectedCuvette, selectedSlits, sampleName });
      socket.emit('startSensorData');
    } else {
      socket.emit('stopSensorData');
    }
    setIsSimulationRunning(!isSimulationRunning); // Toggle l'état de la simulation
  };

  
  // Cette fonction est maintenant ajustée pour envoyer les paramètres et démarrer la génération des données
  const startSensorData = () => {
    if (!wavelengthMin || !wavelengthMax || !step || !selectedCuvette || selectedSlits.length === 0 || !sampleName.trim()) {
      alert("Veuillez remplir tous les champs avant de démarrer.");
      return;
    }
    socket.emit('setScanningParams', { wavelengthMin, wavelengthMax, step, selectedCuvette, selectedSlits, sampleName });
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
        placeholder=" λ_Min [400nm,886nm]"
      />
      <input
        type="number"
        value={wavelengthMax}
        onChange={(e) => setWavelengthMax(e.target.value)}
        placeholder=" λ_Max [400nm,886nm]"
      />
      <input
        type="number"
        value={step}
        onChange={(e) => setStep(e.target.value)}
        placeholder="pas [0.1nm,100nm]"
      />
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
      <input
        type="text"
        value={sampleName}
        onChange={(e) => setSampleName(e.target.value)}
        placeholder="Nom de l'échantillon"
      />
      <button onClick={toggleSensorData}>
        {isSimulationRunning ? "Arrêter" : "Démarrer"}
      </button>
      <button onClick={downloadCsv}>Télécharger CSV</button>
      <button onClick={resetGraphData}>Réinitialiser les données du graphique</button>
    </div>
  );
};

export default ScanningControlPanel;