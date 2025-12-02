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
  return (
    <>
    {(products?.results?.length ?? 0) > 0 && (
      <div className="space-y-2">
        <div  className="bg-white rounded-lg shadow-md p-6">
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