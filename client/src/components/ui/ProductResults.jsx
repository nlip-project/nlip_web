export default function ProductResults({products, isLoading}) {
  return (
    <>
    {(products?.results?.length ?? 0) > 0 && (
        <div className="space-y-2">
          {(products?.results ?? []).map((store) => {
            const storeName = Object.keys(store)[0];
            return (
              <div key={storeName} className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">{storeName}</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {store[storeName].map((product, index) => (
                    <a key={index} href={product.link}>
                      <div className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                        {product.product_photo && (
                          <img
                            src={product.product_photo}
                            alt={product.name}
                            className="w-full h-48 object-contain mb-3 rounded-md"
                          />
                        )}

                        <h3 className="font-semibold text-gray-800 mb-2">
                          {product.name}
                        </h3>

                        {product.description && (
                          <p className="text-sm text-gray-600 mb-2">
                            {product.description}
                          </p>
                        )}

                        <p className="text-lg font-bold text-green-600">
                          ${product.price}
                        </p>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            );
          })}
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