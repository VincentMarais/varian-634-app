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
  // Configuration par défaut pour un graphique vide
  let globalLabels = [''];
  let datasets = [{
    label: 'Aucune donnée',
    data: [null],
    borderColor: 'rgba(0, 0, 0, 0.1)',
    pointBackgroundColor: 'rgba(0, 0, 0, 0.1)',
  }];

  if (AbsorbanceData && AbsorbanceData.length > 0) {
    const groupedData = AbsorbanceData.reduce((acc, data) => {
      const { slitId, data_x, data_y } = data;
      if (!acc[slitId]) acc[slitId] = [];
      acc[slitId].push({ data_x, data_y });
      return acc;
    }, {});

    globalLabels = [...new Set(AbsorbanceData.map(data => data.data_x))].sort((a, b) => Number(a) - Number(b));

    datasets = Object.keys(groupedData).map((slitId, index) => {
      const dataPoints = groupedData[slitId];
      const mappedData = globalLabels.map(label => {
        const dataPoint = dataPoints.find(dp => dp.data_x === label);
        return dataPoint ? dataPoint.data_y : null;
      });

      return {
        label: `Absorbance (${slitId})`,
        data: mappedData,
        fill: false,
        borderColor: `hsl(${index * 90 % 360}, 60%, 50%)`,
        pointBackgroundColor: `hsl(${index * 90 % 360}, 60%, 50%)`,
      };
    });
  }

  const data = { labels: globalLabels, datasets };

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
        text: 'Mode balayage VARIAN 634',
        font: {
          size: 18,
        },
      },
    },
  };

  return (
    <div className="chart-container" style={{ width: '100%', height: '500px' }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default ChartComponent;
