import React from 'react';

function ResultsTable({ results }) {
    if (!results || results.length === 0) return null;

    return (
        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Résultat</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Club</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lieu</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((item, index) => (
                        <tr key={index} className="hover:bg-gray-50 transition-colors duration-150">
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.date}</td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-primary-700">{item.result}</td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{item.club}</td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{item.lieu}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ResultsTable;