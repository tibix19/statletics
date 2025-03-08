import React from 'react';
import { useNavigate } from 'react-router-dom';
import ResultsTable from './ResultsTable';
import ResultsChart from './ResultsChart';

function ResultsDisplay({ initialResults }) {
    const navigate = useNavigate();
    const [allResults, setAllResults] = React.useState(null);
    const [displayedData, setDisplayedData] = React.useState(null);
    const [uniquePersons, setUniquePersons] = React.useState([]);
    const [selectedPerson, setSelectedPerson] = React.useState(null);

    React.useEffect(() => {
        if (initialResults) {
            handleResults(initialResults);
        }
    }, [initialResults]);

    const handleResults = (result) => {
        console.log('Structure complète des résultats reçus:', result);

        if (result.unique_persons) {
            console.log('Plusieurs personnes trouvées:', result.unique_persons);
            setUniquePersons(result.unique_persons);
            setDisplayedData(null);
            setSelectedPerson(null);
            setAllResults(result);
        } else {
            console.log('Résultats directs reçus:', result);
            setAllResults(result);
            setDisplayedData(result);
            setUniquePersons([]);
        }
    };

    const handlePersonClick = async (person) => {
        console.log('Clicking person:', person);

        try {
            const response = await fetch('/api/athlete-results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    athlete_name: person,
                    search_term: allResults.search_term
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            console.log('Received athlete results:', result);

            setDisplayedData(result);
            setSelectedPerson(person);

            navigate(`/results/${encodeURIComponent(allResults.search_term)}/athlete/${encodeURIComponent(person)}`);
        } catch (error) {
            console.error('Error fetching athlete results:', error);
        }
    };

    return (
        <div className="w-full max-w-7x7">
            {uniquePersons.length > 0 && (
                <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                    <h2 className="text-2xl font-semibold mb-4 text-center text-black">
                        Choisissez une personne :
                    </h2>
                    <div className="flex flex-wrap justify-center gap-2">
                        {uniquePersons.map((person, index) => (
                            <button
                                key={index}
                                onClick={() => handlePersonClick(person)}
                                className={`px-4 py-2 rounded ${selectedPerson === person
                                    ? 'bg-blue-500'
                                    : 'bg-gray-200 hover:bg-blue-100'
                                    }`}
                            >
                                {person}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {displayedData && (
                <div className="bg-white p-6 rounded-lg shadow-lg space-y-6">
                    <h2 className="text-2xl font-semibold text-center text-black">
                        {selectedPerson ? `Résultats pour ${selectedPerson}` : `Résultats pour ${displayedData.selected_person}`}
                    </h2>

                    {displayedData.results && displayedData.results.length > 0 && (
                        <div className="space-y-8">
                            {["100", "200", "300", "400", "600", "800", "HJ"].map(discipline => {
                                const disciplineResults = displayedData.results.filter(r => r.discipline === discipline);
                                if (disciplineResults.length === 0) return null;

                                const disciplineChartData = {
                                    labels: disciplineResults.map(r => r.date),
                                    values: disciplineResults.map(r => {
                                        const [minutes, seconds] = (r.result.includes(':') ? r.result.split(':') : ['0', r.result]);
                                        return parseFloat(minutes) * 60 + parseFloat(seconds);
                                    })
                                };

                                return (
                                    <div key={discipline} className="bg-gray-50 p-6 rounded-lg">
                                        <h3 className="text-xl font-semibold mb-4 text-center text-black">
                                            {discipline === 'HJ' ? 'Saut en hauteur' : `${discipline}m`}
                                        </h3>
                                        <div className="overflow-x-auto mb-6">
                                            <ResultsTable results={disciplineResults} />
                                        </div>
                                        <div className="mb-4">
                                            <ResultsChart chartData={disciplineChartData} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default ResultsDisplay;