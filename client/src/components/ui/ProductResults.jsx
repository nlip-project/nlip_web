export default function ProductResults({products, isLoading}) {
  const getStoreLogo = (storeName) => {
    switch (storeName) {
      case 'Amazon Canada':
        return '/static/amazonicon.png';
      case 'Best Buy Canada':
        return '/static/bestbuylogo.png';
      case 'Staples Canada':
        return '/static/stapleslogo.png';
      case 'Home Depot Canada':
        return '/static/homedepotlogo.webp';
      case 'Dellelce Bookstore UWO':
        return '/static/dellelcelogo.jpeg';
      default:
        return null;
    }
  }

  const getStoreResults = () => {
    const storeStats = {};
    (products?.results ?? []).forEach(product => {
      if (product.store) {
        if (!storeStats[product.store]) {
          storeStats[product.store] = {
            count: 0,
            minPrice: Number(product.price),
            maxPrice: Number(product.price),
            totalPrice: 0
          };
        }
        storeStats[product.store].count += 1;
        storeStats[product.store].totalPrice += Number(product.price);
        storeStats[product.store].minPrice = Math.min(storeStats[product.store].minPrice, Number(product.price));
        storeStats[product.store].maxPrice = Math.max(storeStats[product.store].maxPrice, Number(product.price));
      }
    });
    return storeStats;
  }

  const storeStats = getStoreResults();
  return (
    <>
    {(products?.results?.length ?? 0) > 0 && (
      <div className="space-y-2">
        {/* Store stats summary */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h2 className="text-xl font-semibold mb-2">Store Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(storeStats).map(([store, stats]) => (
              <div key={store} className="flex items-center space-x-3">
                <img src={getStoreLogo(store)} alt={store} className="h-8" />
                <div>
                  <div className="font-medium text-gray-800">{store}</div>
                  <div className="text-sm text-gray-600">Products: {stats.count}</div>
                  <div className="text-sm text-gray-600">Min: ${stats.minPrice.toFixed(2)} | Max: ${stats.maxPrice.toFixed(2)}</div>
                  <div className="text-sm text-gray-600">Avg: ${(stats.totalPrice / stats.count).toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(products?.results ?? []).map((product, index) => {
              return (
                <a key={index} href={product.link}>
                  <div className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow relative">
                    {product.store && (
                      <span className="absolute top-2 right-2">
                        <img src={getStoreLogo(product.store)} alt={product.store} className="h-8" />
                      </span>
                    )}

                    <img
                      src={product.product_photo || 'https://cdn.shopify.com/s/files/1/0533/2089/files/placeholder-images-image_large.png?v=1530129081'}
                      alt={product.name}
                      className="w-full h-48 object-contain mb-3 rounded-md"
                    />

                    <h3 className="font-semibold text-gray-800 mb-2">
                      {product.name}
                    </h3>

                    <p className="text-lg font-bold text-green-600">
                      ${product.price}
                    </p>
                  </div>
                </a>
              );
            })}
          </div>
        </div>
      </div>
    )}
    {(products?.results?.length ?? 0) === 0 && !isLoading && (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <p className="text-gray-500">Search for products to see results</p>
      </div>
    )}
    </>
  )
}