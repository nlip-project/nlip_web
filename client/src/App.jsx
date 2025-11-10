import Text from "./components/Text"
import Products from "./components/Products"

function App() {
  const mode = import.meta.env.VITE_APP_MODE;

  if (mode === "text") return <Text />
  if (mode === "products") return <Products />
  if (mode === "images") return <Images />

  return (
    <>
      <Text />
      <Products />
      <Images />
    </>
  )
}

export default App
