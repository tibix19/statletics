import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [searchResults, setSearchResults] = React.useState(null);

  const handleResults = (results) => {
    setSearchResults(results);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen min-w-screen bg-gray-50 flex flex-col items-center justify-start px-2 py-6 md:px-4 md:py-8">
        <header className="w-full bg-primary-700 text-white py-4 mb-8 rounded-lg shadow-md">
          <h1 className="text-3xl md:text-4xl font-bold text-center text-black">Athletics Results Search</h1>
        </header>
        <div className="w-full max-w-md mx-auto">
          <SearchForm onResults={handleResults} />
        </div>
        <div className="mt-8 w-full max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<ResultsDisplay initialResults={searchResults} />} />
            <Route path="/results/:searchTerm/athlete/:athleteName" element={<ResultsDisplay initialResults={searchResults} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;