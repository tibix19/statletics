import React from 'react';
import LoadingOverlay from './LoadingOverlay';

function SearchForm({ onResults }) {
    const [searchTerm, setSearchTerm] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
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
        } finally {
            setIsLoading(false);
        }
    }
    return (
        <>
            <LoadingOverlay isVisible={isLoading} />
            <form onSubmit={handleSubmit} className="flex flex-col items-center space-y-3 max-w-md">
                <input
                    type="text"
                    placeholder="Enter a name"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 text-center text-black"
                    required
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className="border p-3 rounded hover:bg-blue-500 text-white bg-red-500"
                    disabled={isLoading}
                >
                    Search
                </button>
            </form>
        </>
    );
}

export default SearchForm;