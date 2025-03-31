import React from 'react';
import { useNavigate } from 'react-router-dom';
import ResultsTable from './ResultsTable';
import ResultsChart from './ResultsChart';

const disciplines = [
    { code: "50", name: "50m" },
    { code: "60", name: "60m" },
    { code: "80", name: "80m" },
    { code: "100", name: "100m" },
    { code: "150", name: "150m" },
    { code: "200", name: "200m" },
    { code: "300", name: "300m" },
    { code: "400", name: "400m" },
    { code: "600", name: "600m" },
    { code: "800", name: "800m" },
    { code: "1K0", name: "1000m" },
    { code: "1K5", name: "1500m" },
    { code: "MIL", name: "Meile" },
    { code: "2K0", name: "2000m" },
    { code: "3K0", name: "3000m" },
    { code: "5K0", name: "5000m" },
    { code: "10K", name: "10000m" },
    { code: "11H", name: "110m Hürden" },
    { code: "30H", name: "300m Hürden" },
    { code: "40H", name: "400m Hürden" },
    { code: "3SC", name: "3000m Hindernis" },
    { code: "5W", name: "5000m Bahngehen" },
    { code: "10W", name: "10000m Bahngehen" },
    { code: "HJ", name: "Hochsprung" },
    { code: "PV", name: "Stabhochsprung" },
    { code: "LJ", name: "Weitsprung" },
    { code: "TJ", name: "Dreisprung" },
    { code: "SP", name: "Kugelstoss" },
    { code: "DT", name: "Diskuswurf" },
    { code: "HT", name: "Hammerwurf" },
    { code: "JT", name: "Speerwurf" },
    { code: "10H", name: "100m Hürden" },
    { code: "BAL", name: "Ballwurf" },
    { code: "WEZ", name: "Weitsprung Zone" },
    { code: "20H", name: "200m Hürden" },
    { code: "UKC", name: "UBS Kids Cup" }
];

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
        <div className="w-full max-w-7xl mx-auto">
            {uniquePersons.length > 0 && (
                <div className="bg-white shadow-lg rounded-lg p-4 sm:p-6 mb-6 sm:mb-8">
                    <h2 className="text-2xl font-semibold mb-4 sm:mb-6 text-center text-black">
                        Choisissez une personne :
                    </h2>
                    <div className="flex flex-wrap justify-center gap-3">
                        {uniquePersons.map((person, index) => (
                            <button
                                key={index}
                                onClick={() => handlePersonClick(person)}
                                className={`px-4 py-2 rounded-lg transition-all duration-200 ${selectedPerson === person
                                    ? 'bg-primary-600 text-white shadow-md'
                                    : 'bg-gray-100 hover:bg-primary-50 text-gray-800 hover:text-primary-700'
                                    }`}
                            >
                                {person}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {displayedData && (
                <div className="bg-white p-4 sm:p-8 rounded-lg shadow-lg space-y-6 sm:space-y-8">
                    <h2 className="text-2xl sm:text-3xl font-bold text-center text-black">
                        {selectedPerson ? `Résultats pour ${selectedPerson}` : `Résultats pour ${displayedData.selected_person}`}
                    </h2>

                    {displayedData.results && displayedData.results.length > 0 && (
                        <div className="space-y-8 sm:space-y-12">
                            {disciplines.map(discipline => {
                                const disciplineResults = displayedData.results.filter(r => r.discipline === discipline.code);
                                if (disciplineResults.length === 0) return null;

                                const disciplineChartData = {
                                    labels: disciplineResults.map(r => r.date),
                                    values: disciplineResults.map(r => {
                                        // For field events like jumps and throws, we don't need to convert to seconds
                                        const isFieldEvent = ["HJ", "PV", "LJ", "TJ", "SP", "DT", "HT", "JT", "BAL", "WEZ"].includes(discipline.code);
                                        
                                        if (isFieldEvent) {
                                            return parseFloat(r.result.replace(',', '.'));
                                        } else {
                                            const [minutes, seconds] = (r.result.includes(':') ? r.result.split(':') : ['0', r.result]);
                                            return parseFloat(minutes) * 60 + parseFloat(seconds.replace(',', '.'));
                                        }
                                    })
                                };

                                return (
                                    <div key={discipline.code} className="bg-gray-50 p-3 sm:p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
                                        <h3 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-center text-black">
                                            {discipline.name}
                                        </h3>
                                        <div className="overflow-x-auto mb-6 sm:mb-8">
                                            <ResultsTable results={disciplineResults} />
                                        </div>
                                        <div className="mb-2 sm:mb-4">
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