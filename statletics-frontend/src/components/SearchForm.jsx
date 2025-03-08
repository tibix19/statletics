import React from 'react';

function SearchForm({ onResults }) {
    const [searchTerm, setSearchTerm] = React.useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/api/results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_term: searchTerm }),
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
            <button type="submit" className="border p-3 rounded hover:bg-blue-500 text-white bg-red-500">
                Search
            </button>
        </form>
    );
}

export default SearchForm;