import React, { useState } from 'react';

function SearchForm({ onResults }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [discipline, setDiscipline] = useState('100'); // valeur par défaut

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/api/results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_term: searchTerm, discipline }),
            });
            const result = await response.json();
            onResults(result);
        } catch (error) {
            console.error('Error fetching results:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col items-center space-y-3 max-w-md">
            <input
                type="text"
                placeholder="Enter a name"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 text-center text-black"
                required
            />
            <select
                value={discipline}
                onChange={(e) => setDiscipline(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded text-black"
            >
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="300">300</option>
                <option value="400">400</option>
                <option value="600">600</option>
                <option value="800">800</option>
                <option value="HJ">High Jump</option>
            </select>
            <button type="submit" className="border p-3 rounded hover:bg-blue-500 text-white bg-red-500">
                Search
            </button>
        </form>
    );
}

export default SearchForm;
