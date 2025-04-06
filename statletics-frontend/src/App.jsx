import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';
import AthleteResultsPage from './pages/AthleteResultsPage';

function Home() {
  return (
    <div className="min-h-screen min-w-screen bg-gray-50 flex flex-col items-center justify-start px-2 py-6 md:px-4 md:py-8">
      <header className="w-full bg-primary-700 text-white py-4 mb-8 rounded-lg shadow-md">
        <h1 className="text-3xl md:text-4xl font-bold text-center text-black">
          Athletics Results Search
        </h1>
      </header>
      <div className="w-full max-w-md mx-auto">
        <SearchForm />
      </div>
      <div className="mt-8 w-full max-w-7xl mx-auto">
        <ResultsDisplay />
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/athlete/:athleteName" element={<AthleteResultsPage />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;