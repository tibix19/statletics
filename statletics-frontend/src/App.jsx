import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [searchResults, setSearchResults] = React.useState(null);

  const handleResults = (results) => {
    setSearchResults(results);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen min-w-screen bg-gray-100 flex flex-col items-center justify-center px-4 py-8">
        <h1 className="text-4xl font-bold mb-6 text-black">Athletics Results Search</h1>
        <SearchForm onResults={handleResults} />
        <div className="mt-8">
          <ResultsDisplay initialResults={searchResults} />
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
