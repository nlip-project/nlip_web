import { useState } from "react";
import { NLIPClient } from "../../utils/nlip";

export default function SearchForm({ setProducts, isLoading, setIsLoading}) {
  const [query, setQuery] = useState('');
  const nlipClient = new NLIPClient();
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await nlipClient.sendMessage(query.trim(), true)

      if (response && response.results.length > 0) {
        response.results.sort((a,b) => a.price - b.price)
        setProducts(response);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Product Search</h1>
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for products..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-linear-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:from-cyan-600 hover:to-blue-600 disabled:opacity-50"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  )
}