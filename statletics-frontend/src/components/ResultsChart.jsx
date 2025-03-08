import React from 'react';
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
                borderColor: 'rgb(230, 0, 0)',
                backgroundColor: 'rgba(255, 62, 62, 0.1)',
                pointBackgroundColor: 'rgb(230, 0, 0)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(230, 0, 0)',
                borderWidth: 2,
                tension: 0.2
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: 'Inter, sans-serif',
                        size: window.innerWidth < 768 ? 10 : 12
                    },
                    color: '#4b5563'
                }
            },
            title: {
                display: true,
                text: 'Évolution des performances',
                font: {
                    family: 'Inter, sans-serif',
                    size: window.innerWidth < 768 ? 14 : 16,
                    weight: 'bold'
                },
                color: '#1f2937',
                padding: {
                    top: 10,
                    bottom: 20
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                titleColor: '#e60000',
                bodyColor: '#4b5563',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 12,
                displayColors: false,
                bodyFont: {
                    family: 'Inter, sans-serif'
                },
                titleFont: {
                    family: 'Inter, sans-serif',
                    weight: 'bold'
                }
            }
        },
        scales: {
            y: {
                reverse: false,
                grid: {
                    color: 'rgba(226, 232, 240, 0.5)'
                },
                ticks: {
                    font: {
                        family: 'Inter, sans-serif'
                    },
                    color: '#4b5563'
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        family: 'Inter, sans-serif'
                    },
                    color: '#4b5563'
                }
            }
        }
    };

    return (
        <div className="w-full h-64 sm:h-80 p-4 bg-white rounded-lg shadow-sm border border-gray-100">
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