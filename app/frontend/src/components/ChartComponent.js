import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ChartComponent = ({ AbsorbanceData }) => {
  // Générer des labels basés sur l'indice i
  const labels = AbsorbanceData.map((data, index) => `Indice ${index}`);

  const data = {
    labels,
    datasets: [
      {
        label: 'Absorbance',
        data: AbsorbanceData.map(data => data.value),
        fill: true,
        backgroundColor: 'rgb(255, 33, 56)',
        borderColor: 'rgba(255, 125, 71, 1)',
        pointBackgroundColor: 'rgba(255, 99, 71, 2)',
      },
    ],
  };

  const options = {
    scales: {
      x: {
        title: {
          display: true,
          text: 'Longueur d\'onde (nm)',
          color: '#000',
          font: {
            size: 14,
            weight: 'bold',
          },
        }
      },
      y: {
        title: {
          display: true,
          text: 'Absorbance',
          color: '#000',
          font: {
            size: 14,
            weight: 'bold',
          },
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      title: {
        display: true,
        text: 'Scanning Varian 634',
        font: {
          size: 18,
        },
      },
    },
  };

  return (
    <div className="chart-container" style={{ width: '50%', height: '400px' }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default ChartComponent;
