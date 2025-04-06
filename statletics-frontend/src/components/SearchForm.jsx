import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingOverlay from './LoadingOverlay';

function SearchForm() {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [suggestions, setSuggestions] = React.useState([]);
    const [errorMessage, setErrorMessage] = React.useState('');
    const [selectedAthlete, setSelectedAthlete] = React.useState(null);

    const fetchSuggestions = async (term) => {
        try {
            const response = await fetch('/api/results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_term: term }),
            });
            const result = await response.json();
            if (result.unique_persons) {
                setSuggestions(result.unique_persons);
            } else {
                setSuggestions([]);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    };

    const handleChange = (e) => {
        const term = e.target.value;
        setSearchTerm(term);
        setErrorMessage('');
        setSelectedAthlete(null);
        if (term.length >= 2) {
            fetchSuggestions(term);
        } else {
            setSuggestions([]);
        }
    };

    const handleSuggestionClick = (athlete) => {
        setSelectedAthlete(athlete);
        navigate(`/athlete/${encodeURIComponent(athlete)}`);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!selectedAthlete) {
            setErrorMessage("Aucun athlète sélectionné");
            return;
        }
        navigate(`/athlete/${encodeURIComponent(selectedAthlete)}`);
    };

    return (
        <>
            <LoadingOverlay isVisible={isLoading} />
            <form onSubmit={handleSubmit} className="w-full flex flex-col items-center space-y-4">
                <div className="w-full relative">
                    <input
                        type="text"
                        placeholder="Enter a name"
                        value={searchTerm}
                        onChange={handleChange}
                        className="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-left text-black transition-all duration-200 ease-in-out"
                        required
                        disabled={isLoading}
                    />
                    {suggestions.length > 0 && (
                        <ul className="absolute left-0 right-0 bg-white border border-gray-300 rounded-b-lg max-h-40 overflow-y-auto z-10">
                            {suggestions.map((athlete, index) => (
                                <li
                                    key={index}
                                    onClick={() => handleSuggestionClick(athlete)}
                                    className="px-3 py-2 hover:bg-primary-100 cursor-pointer text-black"
                                >
                                    {athlete}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
                {errorMessage && (
                    <div className="text-red-600 text-center">
                        {errorMessage}
                    </div>
                )}
            </form>
        </>
    );
}

export default SearchForm;