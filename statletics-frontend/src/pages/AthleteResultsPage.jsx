import React from 'react';
import { useParams } from 'react-router-dom';
import ResultsDisplay from '../components/ResultsDisplay';
import LoadingOverlay from '../components/LoadingOverlay'; // added import

function AthleteResultsPage() {
    const { athleteName } = useParams();
    const [data, setData] = React.useState(null);
    const [isLoading, setIsLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchResults = async () => {
            try {
                const response = await fetch('/api/athlete-results', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        athlete_name: athleteName,
                        search_term: athleteName
                    }),
                });
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error('Error fetching athlete results:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchResults();
    }, [athleteName]);

    if (isLoading) {
        return <LoadingOverlay isVisible={isLoading} />;
    }

    return (
        <div className="min-h-screen bg-gray-50 px-4 py-6">
            <header className="mb-8">
                <h2 className="text-3xl text-center font-bold text-black">
                    Results for {athleteName}
                </h2>
            </header>
            <div className="max-w-7xl mx-auto">
                <ResultsDisplay initialResults={data} />
            </div>
        </div>
    );
}

export default AthleteResultsPage;
