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
            <form onSubmit={handleSubmit} className="w-full flex flex-col items-center space-y-4">
                <div className="w-full relative">
                    <input
                        type="text"
                        placeholder="Enter a name"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-center text-black transition-all duration-200 ease-in-out"
                        required
                        disabled={isLoading}
                    />
                </div>
                <button
                    type="submit"
                    className="px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium shadow-md transition-all duration-200 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed text-black"
                    disabled={isLoading}
                >
                    Search
                </button>
            </form>
        </>
    );
}

export default SearchForm;