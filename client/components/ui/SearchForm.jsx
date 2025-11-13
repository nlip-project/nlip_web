import { useState } from "react";
import { NLIPClient } from "../../utils/nlip";
//import {runModule} from "../../utils/module_test"


export default function SearchForm({ setProducts, isLoading, setIsLoading}) {
  const [query, setQuery] = useState('');
  const nlipClient = new NLIPClient();
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await nlipClient.sendMessage(query.trim())
      //const response = '{"Best Buy":[{"name":"Dell XPS 15","price":1299.99,"description":"15.6-inch FHD display, Intel Core i7, 16GB RAM, 512GB SSD"},{"name":"HP Pavilion 14","price":649.99,"description":"14-inch HD display, AMD Ryzen 5, 8GB RAM, 256GB SSD"}],"Amazon":[{"name":"Lenovo ThinkPad X1 Carbon","price":1549.99,"description":"14-inch 2K display, Intel Core i7, 16GB RAM, 1TB SSD, Business laptop"},{"name":"ASUS VivoBook 15","price":529.99,"description":"15.6-inch FHD display, Intel Core i5, 12GB RAM, 512GB SSD"}],"Walmart":[{"name":"Acer Aspire 5","price":479.99,"description":"15.6-inch FHD display, AMD Ryzen 3, 8GB RAM, 256GB SSD"},{"name":"Microsoft Surface Laptop 5","price":1199.99,"description":"13.5-inch PixelSense touchscreen, Intel Core i5, 8GB RAM, 256GB SSD"}]}';

      console.log(response)

      const data = JSON.parse(response);

      if (data) {
        setProducts(data);
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