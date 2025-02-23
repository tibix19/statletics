// import React from 'react';
import { Line } from 'react-chartjs-2';
import PropTypes from 'prop-types';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
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

function ResultsChart({ chartData }) {
    if (!chartData || !chartData.labels) return null;

    const data = {
        labels: chartData.labels,
        datasets: [
            {
                label: 'Performance',
                data: chartData.values,
                borderColor: 'rgb(202, 51, 51)',
                tension: 0.1
            }
        ]
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Évolution des performances'
            }
        },
        scales: {
            y: {
                reverse: false // Pour le 100m, un temps plus bas est meilleur
            }
        }
    };

    return (
        <div className="w-full p-4 bg-white rounded-lg shadow">
            <Line data={data} options={options} />
        </div>
    );
}

ResultsChart.propTypes = {
    chartData: PropTypes.shape({
        labels: PropTypes.arrayOf(PropTypes.string).isRequired,
        values: PropTypes.arrayOf(PropTypes.number).isRequired,
    }).isRequired,
};

export default ResultsChart;