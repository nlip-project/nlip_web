import { useState } from 'react';
import SearchForm from './ui/SearchForm';
import ProductResults from './ui/ProductResults';

export default function Products() {
  const [products, setProducts] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <SearchForm isLoading={isLoading} setProducts={setProducts} setIsLoading={setIsLoading} />
        <ProductResults products={products} isLoading={isLoading} />
      </div>
    </div>
  );
}