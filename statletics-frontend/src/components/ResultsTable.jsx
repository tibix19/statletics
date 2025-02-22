import React from 'react';

function ResultsTable({ results }) {
    if (!results || results.length === 0) return null;

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Résultat</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Club</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Lieu</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((item, index) => (
                        <tr key={index}>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{item.date}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">{item.result}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">{item.club}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">{item.lieu}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ResultsTable;
